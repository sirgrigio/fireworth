export class CategoryGroup {
    categoryGroupId: number;
    name: string;
    categories?: Category[];

    constructor(categoryGroupId: number, name: string, categories?: Category[]) {
        this.categoryGroupId = categoryGroupId;
        this.name = name;
        this.categories = categories;
    }
}

export class Category {
    categoryId: number;
    categoryGroupId: number;
    categoryGroupName: string;
    name: string;

    constructor(categoryId: number, categoryGroupId: number, categoryGroupName: string, name: string) {
        this.categoryId = categoryId;
        this.categoryGroupId = categoryGroupId;
        this.categoryGroupName = categoryGroupName;
        this.name = name;
    }

    public toString(): string {
        return `${this.categoryGroupName}: ${this.name}`;
    }
}
