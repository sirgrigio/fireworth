import logging
from abc import ABC, abstractmethod
from decimal import getcontext
from typing import List, NamedTuple, Set

from beancount.core.data import Meta, Posting

from src.modules.ynab.api.models.transactions import \
    Subtransaction as YNABSubtransaction
from src.modules.ynab.api.models.transactions import \
    Transaction as YNABTransaction
from src.modules.ynab.beancount.builders import (BeanPostingBuilder,
                                                 BeanTransactionBuilder)
from src.modules.ynab.beancount.preprocessors import Preprocessor
from src.modules.ynab.beancount.settings import Settings
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

    @abstractmethod
    def postify(self, include_meta=True) -> List[Posting]:
        raise NotImplementedError()

    @abstractmethod
    def beanify(self) -> NamedTuple:
        raise NotImplementedError()

    @staticmethod
    def factory(txn: YNABTransaction, settings: Settings=None) -> "YNABBeanifier":
        if txn.transfer_account_id:
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

    def beanify(self) -> NamedTuple:
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
            src_acc = self.settings.mapper_expenses.map(self.txn.payee_name)
        return self._postify(
            self.txn.amount,
            src_accs=[src_acc],
            dst_accs=[self.settings.mapper_accounts.map(self.txn.account_name)],
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> NamedTuple:
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
            self.txn.amount,
            src_accs=src_accs,
            dst_accs=dst_accs,
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> NamedTuple:
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
        src_accs = [self.settings.mapper_accounts.map(self.txn.account_name)]
        dst_accs = [self.settings.mapper_accounts.map(self.txn.payee_name.split(':')[1].strip())]
        recipients = self._get_recipients()
        if recipients:
            if self.txn.account_name in self.settings.xfer_ynab_lending_accounts:
                src_accs = [f'{src_accs[0]}:{r}' for r in recipients]
            if any([self.txn.payee_name == f'Transfer : {a}' for a in self.settings.xfer_ynab_lending_accounts]):
                dst_accs = [f'{dst_accs[0]}:{r}' for r in recipients]
        return self._postify(
            self.txn.amount,
            src_accs=src_accs,
            dst_accs=dst_accs,
            meta=self._get_meta() if include_meta else None
        )

    def beanify(self) -> NamedTuple:
        builder = BeanTransactionBuilder()
        builder.set_date(self.txn.date)
        builder.set_tags(self._get_tags())
        builder.set_meta(self._get_meta())
        builder.set_narration(self.txn.memo)
        txns_to_postify = self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        for t in txns_to_postify:
            for p in YNABBeanifier.factory(t, self.settings).postify(include_meta=len(txns_to_postify)>1):
                builder.add_posting(p)
        postings = builder.current_postings()



        return builder.build()


def beanify(settings: Settings, transactions: List[YNABTransaction]) -> List[NamedTuple]:
    assert settings is not None
    assert transactions is not None
    assert len(transactions) > 0
    getcontext().prec = 60
    beancount_transactions = []
    handled_transfers = []
    handled_transactions = []
    for t in transactions:
        log.debug(f'handling transaction: {t.describe(sep=" >> ")}')
        if t.id not in handled_transfers:
            processed_t = Preprocessor.apply(settings.preprocessors, t)
            log.debug(f'preprocessed transaction: {processed_t.describe(sep=" >> ")}')
            if any([c.match(processed_t) for c in settings.skip_conditions]):
                log.info(f'skipping transaction: {processed_t.describe(sep=" >> ")}')
                continue
            try:
                btxn = YNABBeanifier.factory(processed_t, settings).beanify()
                beancount_transactions.append(btxn)
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
