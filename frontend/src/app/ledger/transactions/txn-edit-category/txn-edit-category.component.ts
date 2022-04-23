import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, TemplateRef, ViewChild } from '@angular/core';
import { Category } from 'src/app/shared/models/category.model';
import { Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-category',
  templateUrl: './txn-edit-category.component.html',
  styleUrls: ['./txn-edit-category.component.scss']
})
export class TxnEditCategoryComponent implements OnInit, OnChanges {

  @ViewChild('typehead') typeheadRef?: ElementRef;

  @Input() transaction?: Transaction;
  @Input() categories?: Category[];
  @Input() readonly: boolean = true;
  @Input() required: boolean = true;

  @Output() categoryChange: EventEmitter<Category> = new EventEmitter();

  _preview?: Category;

  constructor() { }

  ngOnInit(): void {
    this.updatePreview();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.typeheadRef) {
      if (changes.transaction.currentValue) {
        this.typeheadRef.nativeElement.value = changes.transaction.currentValue.category?.toString() ?? null;
      }
    }
    if (!changes.readonly.firstChange && changes.readonly.currentValue) {
      this.updatePreview();
    }
  }

  private updatePreview() {
    this._preview = this.transaction?.category ?? undefined;
  }

  onCategoryChange(category?: Category) {
    this._preview = category;
    this.categoryChange.emit(category);
  }

  onBlur() {
    this.categoryChange.emit(this._preview);
    if (!this._preview && this.typeheadRef) {
      this.typeheadRef.nativeElement.value = null;
    }
  }

  get _wrappedCategories(): { nameId: string, group: string, category: Category }[] | undefined {
    return this.categories?.map(e => {
      return { 'nameId': e.toString(), 'group': e.categoryGroupName, 'category': e };
    });
  }
}
