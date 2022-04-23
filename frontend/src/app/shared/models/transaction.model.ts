import { DateTime } from "luxon";
import { Category } from "./category.model";

type PayeeType = 'EXPENSE' | 'INCOME' | 'TRANSFER' | 'TRADE';

export class Payee {
    payeeId: number;
    type: PayeeType;
    name: string;
    linkedAccountId?: number | null;

    constructor(
        payeeId: number,
        type: PayeeType,
        name: string,
        linkedAccountId?: number | null) {
        this.payeeId = payeeId;
        this.type = type;
        this.name = name;
        this.linkedAccountId = linkedAccountId;
    }

    get isExpense(): boolean {
        return this.type == 'EXPENSE';
    }

    get isIncome(): boolean {
        return this.type == 'INCOME';
    }

    get isTransfer(): boolean {
        return this.type == 'TRANSFER';
    }

    get isTrade(): boolean {
        return this.type == 'TRADE';
    }
}

export class Transaction {
    transactionId?: number | null;
    date?: DateTime | null;
    accountId?: number | null;
    accountName?: string | null;
    payee?: Payee | null;
    category?: Category | null;
    memo?: string | null;
    currency?: string | null;
    amount?: number | null;
    exchangeRate?: number | null;
    unitPrice?: number | null;
    quantity?: number | null;
    linkedTransactionId?: number | null;

    static make(
        transactionId?: number | null,
        date?: DateTime | null,
        accountId?: number | null,
        accountName?: string | null,
        payee?: Payee | null,
        category?: Category | null,
        memo?: string | null,
        currency?: string | null,
        amount?: number | null,
        exchangeRate?: number | null,
        unitPrice?: number | null,
        quantity?: number | null,
        linkedTransactionId?: number | null) {
        return new Transaction({
            transactionId: transactionId ?? null,
            accountId: accountId ?? null,
            accountName: accountName ?? null,
            payee: payee ?? null,
            category: category ?? null,
            memo: memo ?? null,
            date: date ?? null,
            currency: currency ?? null,
            amount: amount ?? null,
            exchangeRate: exchangeRate ?? null,
            unitPrice: unitPrice ?? null,
            quantity: quantity ?? null,
            linkedTransactionId: linkedTransactionId ?? null,
        });
    }

    constructor(props: Partial<Transaction> = {}) {
        Object.assign(this, props);
    }

    get isExpense(): boolean {
        return this.payee?.isExpense ?? true;
    }
}
