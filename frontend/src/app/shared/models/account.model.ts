export class AccountTypeGroup {
    accountTypeGroupId: number;
    name: string;
    accountTypes?: AccountType[];

    constructor(accountTypeGroupId: number, name: string, accountTypes?: AccountType[]) {
        this.accountTypeGroupId = accountTypeGroupId;
        this.name = name;
        this.accountTypes = accountTypes;
    }
}

export class AccountType {
    accountTypeId: number;
    accountTypeGroupId: number;
    name: string;

    constructor(accountTypeId: number, accountTypeGroupId: number, name: string) {
        this.accountTypeId = accountTypeId;
        this.accountTypeGroupId = accountTypeGroupId;
        this.name = name;
    }
}

export class Account {
    accountId: number;
    accountTypeId: number;
    accountTypeGroupName: string;
    accountTypeName: string;
    name: string;
    currency: string;
    allocation: Map<string, number>;
    symbol?: string | null;
    isin?: string | null;
    ter?: number | null;
    capitalGainTaxRate?: number | null;

    constructor(
        accountId: number,
        accountTypeId: number,
        accountTypeGroupName: string,
        accountTypeName: string,
        name: string,
        currency: string,
        allocation: Map<string, number>,
        symbol?: string | null,
        isin?: string | null,
        ter?: number | null,
        capitalGainTaxRate?: number | null) {
        this.accountId = accountId;
        this.accountTypeId = accountTypeId;
        this.accountTypeGroupName = accountTypeGroupName;
        this.accountTypeName = accountTypeName;
        this.name = name;
        this.currency = currency;
        this.allocation = allocation;
        this.symbol = symbol;
        this.isin = isin;
        this.ter = ter;
        this.capitalGainTaxRate = capitalGainTaxRate;
    }

    get isCash(): boolean {
        return this.accountTypeName == 'cash';
    }

    get isNonCashAsset(): boolean {
        return this.accountTypeName == 'property' || this.accountTypeName == 'security';
    }

    get isCredit(): boolean {
        return this.accountTypeName == 'credit'
    }
}
