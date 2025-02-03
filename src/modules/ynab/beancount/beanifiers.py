import datetime
import logging
import math
from abc import ABC, abstractmethod
from decimal import getcontext
from typing import Dict, List, Set

from beancount.core.data import Meta, Posting

from src.modules.ynab.api.models.transactions import \
    Subtransaction as YNABSubtransaction
from src.modules.ynab.api.models.transactions import \
    Transaction as YNABTransaction
from src.modules.ynab.beancount.builders import (BeanPostingBuilder,
                                                 BeanTransactionBuilder)
from src.modules.ynab.beancount.mergers import Merger
from src.modules.ynab.beancount.processors import Processor
from src.modules.ynab.beancount.settings import Settings
from src.modules.ynab.beancount.utils.beancount import (BeancountOpen,
                                                        BeancountTransaction)
from src.modules.ynab.beancount.utils.fi_transaction import (
    FITransaction, MaturityTransaction, SellTransaction)
from src.modules.ynab.beancount.utils.numbers import get_precision
from src.modules.ynab.beancount.utils.strings import camelcased, lowerdashed

log = logging.getLogger(__name__)


class YNABBeanifier(ABC):

    def __init__(
            self,
            txn: YNABTransaction | YNABSubtransaction,
            settings: Settings=None,
        ):
        self.txn = txn
        self.settings = settings

    def _get_tags(self) -> Set[str]:
        tags = set()
        for xtr in self.settings.extractors_tags:
            tags = tags.union([lowerdashed(t) for t in xtr.extract(self.txn, [])])
        return tags

    def _get_meta(self) -> Meta:
        meta = dict()
        for xtr in self.settings.extractors_meta:
            for k, v in xtr.extract(self.txn, {}).items():
                meta[lowerdashed(k)] = lowerdashed(v)
        return meta

    def _get_recipients(self) -> Set[str]:
        recipients = set()
        for xtr in self.settings.extractors_recipients:
            recipients = recipients.union([camelcased(r) for r in xtr.extract(self.txn, [])])
        return recipients

    def _postify(self, amount: int, src_accs: List[str]=[], dst_accs: List[str]=[], meta: Meta=None) -> List[Posting]:
        assert len(src_accs) > 0
        assert len(dst_accs) > 0
        amount = amount / 1000  # YNAB stores amounts using a 1000 multiplier
        postings = []
        builder = BeanPostingBuilder()
        builder.set_units(-amount / len(src_accs))
        for acc in src_accs:
            postings.append(builder.set_account(acc).build(clear=False))
        builder.set_meta(meta)
        builder.set_units(amount / len(dst_accs))
        for acc in dst_accs:
            postings.append(builder.set_account(acc).build(clear=False))
        return postings

    def _postify_fi_txn(
            self,
            date: datetime.date=None,
            symbol: str=None,
            quantity: float=None,
            unit_price: float=None,
            currency: str=None,
            src_acc: str=None,
            dst_acc: str=None,
            meta: Meta=None,
            pnl_acc: str=None,
    ) -> List[Posting]:
        assert date is not None
        assert symbol is not None
        assert src_acc is not None
        assert dst_acc is not None
        postings = []
        builder = BeanPostingBuilder()
        q_precision = get_precision(quantity)
        p_precision = max(get_precision(unit_price), 2)
        builder.set_account(src_acc)
        builder.set_units(-quantity * unit_price, currency=currency, precision=max(q_precision, p_precision))
        builder.set_meta(meta)
        postings.append(builder.build())
        builder.set_account(dst_acc)
        builder.set_units(quantity, currency=symbol, precision=q_precision)
        if quantity > 0:
            # it's a buy operation at a certain cost
            builder.set_cost(date, unit_price, currency=currency, precision=p_precision)
        else:
            # it's a sell operation at a certain price: use average booking
            builder.set_price(unit_price, currency=currency, precision=p_precision)
            builder.set_costspec(merge=True)
        builder.set_meta(meta)
        postings.append(builder.build())
        if pnl_acc is not None:
            builder = BeanPostingBuilder()
            builder.set_account(pnl_acc)
            postings.append(builder.build())
        return postings

    @abstractmethod
    def postify(self, include_meta=True) -> List[Posting]:
        raise NotImplementedError()

    @abstractmethod
    def beanify(self) -> BeancountTransaction:
        raise NotImplementedError()

    @staticmethod
    def factory(txn: YNABTransaction, settings: Settings=None) -> "YNABBeanifier":
        if txn.payee_name == 'Transfer : Investments':
            return InvestmentBeanifier(txn, settings=settings)
        elif txn.transfer_account_id:
            return TransferBeanifier(txn, settings=settings)
        elif txn.amount > 0:
            return InflowBeanifier(txn, settings=settings)
        else:
            return ExpenseBeanifier(txn, settings=settings)


class ExpenseBeanifier(YNABBeanifier):

    def postify(self, include_meta=True) -> List[Posting]:
        return self._postify(
            -self.txn.amount,
            src_accs=[self.settings.mapper_accounts.map(self.txn.account_name)],
            dst_accs=[self.settings.mapper_expenses.map((self.txn.category_name, self.txn.payee_name), default_key='.')],
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> BeancountTransaction:
        builder = BeanTransactionBuilder()
        builder.set_date(self.txn.date)
        builder.set_tags(self._get_tags())
        builder.set_meta(self._get_meta())
        builder.set_payee(self.txn.payee_name.strip())
        builder.set_narration(self.txn.memo)
        txns_to_postify = self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        for t in txns_to_postify:
            for p in YNABBeanifier.factory(t, self.settings).postify(include_meta=len(txns_to_postify)>1):
                builder.add_posting(p)
        return builder.build()


class InflowBeanifier(YNABBeanifier):

    def postify(self, include_meta=True) -> List[Posting]:
        src_acc = self.settings.mapper_inflows.map(self.txn.payee_name)
        if not src_acc:
            log.warning(f'cannot properly map inflow: {self.txn.describe(sep=" >> ")}')
            log.warning('trying to map it using expenses assuming it is a refund')
            src_acc = self.settings.mapper_expenses.map((self.txn.category_name, self.txn.payee_name), default_key='.')
        return self._postify(
            self.txn.amount,
            src_accs=[src_acc],
            dst_accs=[self.settings.mapper_accounts.map(self.txn.account_name)],
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> BeancountTransaction:
        builder = BeanTransactionBuilder()
        builder.set_date(self.txn.date)
        builder.set_tags(self._get_tags())
        builder.set_meta(self._get_meta())
        builder.set_payee(self.txn.payee_name.strip())
        builder.set_narration(self.txn.memo)
        txns_to_postify = self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        for t in txns_to_postify:
            for p in YNABBeanifier.factory(t, self.settings).postify(include_meta=len(txns_to_postify)>1):
                builder.add_posting(p)
        return builder.build()


class TransferBeanifier(YNABBeanifier):

    def postify(self, include_meta=True) -> List[Posting]:
        src_accs = [self.settings.mapper_accounts.map(self.txn.account_name)]
        dst_accs = [self.settings.mapper_accounts.map(self.txn.payee_name.split(':')[1].strip())]
        recipients = self._get_recipients()
        if recipients:
            if self.txn.account_name in self.settings.xfer_ynab_lending_accounts:
                src_accs = [f'{src_accs[0]}:{r}' for r in recipients]
            if any([self.txn.payee_name == f'Transfer : {a}' for a in self.settings.xfer_ynab_lending_accounts]):
                dst_accs = [f'{dst_accs[0]}:{r}' for r in recipients]
        return self._postify(
            -self.txn.amount,
            src_accs=src_accs,
            dst_accs=dst_accs,
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> BeancountTransaction:
        builder = BeanTransactionBuilder()
        builder.set_date(self.txn.date)
        builder.set_tags(self._get_tags())
        builder.set_meta(self._get_meta())
        txns_to_postify = self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        for t in txns_to_postify:
            for p in YNABBeanifier.factory(t, self.settings).postify(include_meta=len(txns_to_postify)>1):
                builder.add_posting(p)
        postings = builder.current_postings()
        if any([p.account.startswith('Liabilities') and p.units.number > 0 for p in postings]):
            builder.set_payee(self.settings.xfer_default_payment_payee)
        elif any([p.account.startswith('Liabilities') and p.units.number < 0 for p in postings]):
            builder.set_payee(self.settings.xfer_default_borrowing_payee)
        elif all([p.account.startswith('Assets') for p in postings]):
            if any([
                any([
                    p.account.startswith(acc)
                    for acc in self.settings.xfer_lending_accounts
                ])
                and p.units.number > 0
                for p in postings
            ]):
                builder.set_payee(self.settings.xfer_default_lending_payee)
            elif any([
                any([
                    p.account.startswith(acc)
                    for acc in self.settings.xfer_lending_accounts
                ])
                and p.units.number < 0
                for p in postings
            ]):
                builder.set_payee(self.settings.xfer_default_payback_payee)
            else:
                builder.set_payee(self.settings.xfer_default_payee)
        else:
            builder.set_payee(self.txn.payee_name)
        # set memo after recipients have been extracted
        builder.set_narration(self.txn.memo)
        return builder.build()


class InvestmentBeanifier(YNABBeanifier):

    def postify(self, include_meta=True) -> List[Posting]:
        fitxn: FITransaction = None
        for parser in self.settings.parsers:
            fitxn: FITransaction = parser.parse(self.txn)
            if fitxn:
                break
        assert fitxn is not None

        if self.txn.account_name in self.settings.xfer_ynab_financial_instrument_accounts and not self.txn.transfer_account_id:
            src_acc = self.settings.mapper_accounts.map(fitxn.src_acc or fitxn.symbol or fitxn.xcurr_a)
            dst_acc = self.settings.mapper_accounts.map(fitxn.dst_acc or fitxn.symbol or fitxn.xcurr_a)
        elif self.txn.account_name not in self.settings.xfer_ynab_financial_instrument_accounts:
            src_acc = self.settings.mapper_accounts.map(fitxn.src_acc or self.txn.account_name)
            dst_acc = self.settings.mapper_accounts.map(fitxn.dst_acc or fitxn.symbol or fitxn.xcurr_a)

        pnl_acc = None
        if isinstance(fitxn, SellTransaction) or isinstance(fitxn, MaturityTransaction):
            pnl_acc = self.settings.mapper_pnl.map(dst_acc)

        return self._postify_fi_txn(
            date=self.txn.date,
            symbol=fitxn.symbol,
            quantity=fitxn.quantity,
            unit_price=fitxn.unit_price,
            currency=fitxn.currency,
            src_acc=src_acc,
            dst_acc=dst_acc,
            meta=self._get_meta() if include_meta else None,
            pnl_acc=pnl_acc
        )

    def beanify(self) -> BeancountTransaction:
        builder = BeanTransactionBuilder()
        builder.set_date(self.txn.date)
        builder.set_tags(self._get_tags())
        builder.set_meta(self._get_meta())
        builder.set_narration(self.txn.memo)
        txns_to_postify = self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        for t in txns_to_postify:
            for p in YNABBeanifier.factory(t, self.settings).postify(include_meta=len(txns_to_postify)>1):
                builder.add_posting(p)
        builder.set_payee('FinInstTxn')
        builder.set_narration(self.txn.memo)
        return builder.build()


def __normalize_transfers(transactions: List[YNABTransaction]) -> Dict[str, str]:
    byid = {}
    for t in transactions:
        for s in t.subtransactions + [t] if t.subtransactions else [t]:
            byid[s.id] = s
    transfer_types = {}
    for t in transactions:
        if t.transfer_transaction_id:
            transfer_types[t.id] = 'Transaction'
            byid[t.transfer_transaction_id].transfer_transaction_id = t.id
        for s in t.subtransactions:
            if s.transfer_transaction_id:
                transfer_types[s.id] = 'Subtransaction'
                byid[s.transfer_transaction_id].transfer_transaction_id = s.id
    return transfer_types


def beanify(settings: Settings, transactions: List[YNABTransaction]) -> List[BeancountTransaction]:
    assert settings is not None
    assert transactions is not None
    assert len(transactions) > 0
    getcontext().prec = 60
    transfer_types = __normalize_transfers(transactions)
    beancount_transactions = []
    handled_accounts = set()
    handled_transfers = []
    handled_transactions = []
    log.debug(f'applying mergers before processing single transactions')
    transactions = Merger.apply(settings.mergers, transactions)
    for t in transactions:
        log.debug(f'handling transaction: {t.describe(sep=" >> ")}')
        if t.id not in handled_transfers:
            processed_t = Processor.apply(settings.preprocessors, t)
            log.debug(f'preprocessed transaction: {processed_t.describe(sep=" >> ")}')
            if any([c.match(processed_t) for c in settings.skip_conditions]):
                log.info(f'skipping transaction: {processed_t.describe(sep=" >> ")}')
                continue
            try:
                if transfer_types.get(t.transfer_transaction_id, None) == 'Subtransaction':
                    log.debug(f'skipping transfer to be handled as subtransaction: {processed_t.describe(sep=" >> ")}')
                    continue
                btxn: BeancountTransaction = YNABBeanifier.factory(processed_t, settings).beanify()
                p_btxn: BeancountTransaction = Processor.apply(settings.postprocessors, btxn)
                for posting in p_btxn.postings:
                    if posting.account not in handled_accounts:
                        beancount_transactions.append(BeancountOpen(p_btxn.date, posting.account).to_open())
                        handled_accounts.add(posting.account)
                beancount_transactions.append(p_btxn.to_transaction())
                handled_transactions.append(t.id)
                for subt in (t.subtransactions + [t] if t.subtransactions else [t]):
                    if subt.transfer_transaction_id:
                        log.debug(f'transaction is a transfer - marking other side as handled')
                        handled_transfers.append(subt.transfer_transaction_id)
                log.debug(f'transaction handled successfully')
            except Exception as ex:
                log.error(f'error handling transaction {t.describe(sep=" >> ")}')
                raise ex
        else:
            log.debug(f'transaction has been already handled {t.describe(sep=" >> ")}')
    for t in transactions:
        if t.id not in handled_transactions and t.id not in handled_transfers:
            log.warning(f'unhandled transaction: {t.describe(sep=" >> ")}')
    return beancount_transactions
