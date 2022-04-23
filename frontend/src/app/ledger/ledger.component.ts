import { Component, OnInit } from '@angular/core';
import { Account } from '../shared/models/account.model';
import { Category } from '../shared/models/category.model';
import { Payee, Transaction } from '../shared/models/transaction.model';
import { LedgerService } from './services/ledger.service';

@Component({
  selector: 'app-ledger',
  templateUrl: './ledger.component.html',
  styleUrls: ['./ledger.component.scss']
})
export class LedgerComponent implements OnInit {

  accounts: Account[] = [];
  payees: Payee[] = [];
  categories: Category[] = [];
  transactions: Transaction[] = [];
  accountFrequencyTable: {[payeeId: number]: Account} = {};
  categoryFrequencyTable: {[payeeId: number]: Category} = {};


  constructor(private ledgerService: LedgerService) { }

  ngOnInit(): void {
    this.accounts = this.ledgerService.getAccounts();
    this.payees = this.ledgerService.getPayees();
    this.categories = this.ledgerService.getCategoryGroups().map(e => e.categories || []).reduce((a, b) => a.concat(b));
    this.transactions = this.ledgerService.getTransations();
    this.transactions.forEach(
      e => {
        this.accountFrequencyTable[e.payee!.payeeId] = this.accounts.find(a => a.accountId == e.accountId)!;
        this.categoryFrequencyTable[e.payee!.payeeId] = e.category!;
      }
    );

  }

  onSmartInput(transaction: Transaction) {
    console.log(transaction);
    this.transactions = [transaction, ...this.transactions];
  }
}
