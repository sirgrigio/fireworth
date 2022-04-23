import { Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { faBolt, faPlus } from '@fortawesome/free-solid-svg-icons';
import { DateTime } from 'luxon';
import { Account } from 'src/app/shared/models/account.model';
import { Category } from 'src/app/shared/models/category.model';
import { Payee, Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-transaction-smart-input',
  templateUrl: './transaction-smart-input.component.html',
  styleUrls: ['./transaction-smart-input.component.scss']
})
export class TransactionSmartInputComponent implements OnInit {

  @ViewChild('smartInput') _smartInput!: ElementRef;

  @Input() accounts: Account[] = [];
  @Input() payees: Payee[] = [];
  @Input() accountFrequencyTable: { [payeeId: number]: Account } = {};
  @Input() categoryFrequencyTable: { [payeeId: number]: Category } = {};

  @Output() smartInput = new EventEmitter<Transaction>();

  faPlus = faPlus;
  faBolt = faBolt;

  _processedInput: string = '';
  _composingTxn: {[key: string]: any} = {};

  _parsers: {[parser: string]: ({prop: string, parse: (arg: string) => any, transform: (arg: string) => string} | null)[]} = {
    'EXPENSE': [
      {
        prop: 'amount',
        parse: (x: string) => -Number.parseFloat(x),
        transform: (x: string) => `<!-- parsed:${x} --><span class="fw-bold">${x}</span>`,
      },
      null,
      {
        prop: 'payee',
        parse: (x: string) => this.payees.find(e => e.name.toLowerCase() == x.toLowerCase()),
        transform: (x: string) => `<!-- parsed:${x} --><span class="fw-bold text-light bg-primary text-capitalize">${x}</span>`,
      }
    ],
  }

  constructor() { }

  ngOnInit(): void {
  }

  onInputChange(html?: string | null) {
    console.log(html);
    if (html) {
      let richText = this._smartInput.nativeElement;
      let offset = Cursor.getCurrentCursorPosition(richText);
      let tokens = html?.trim().replace(/  */, ' ').toLowerCase().split(' ');
      if (tokens[0].includes('spent')) {
        if (!tokens[0].startsWith('<!-- parsed')) {
          tokens[0] = `<!-- parsed:${tokens[0]} --><span class="text-primary" style="font-family: 'Montserrat';">${tokens[0]}</span>`;
        }
        const parser = this._parsers['EXPENSE'];
        for (let i = 0; i < tokens.length-1; i++) {
          const element = tokens[i+1];
          if (parser[i] != null && !tokens[i+1].startsWith('<-- parsed')) {
            const result = parser[i]!.parse(element);
            if (result) {
              this._composingTxn[parser[i]!.prop] = result;
              tokens[i+1] = parser[i]!.transform(tokens[i+1]);
            }
          }
        }
      }
      console.log(tokens);
      this._processedInput = tokens.join(' ') + ' ';
      setTimeout(() => {
        // insert code here that does stuff to the innerHTML, such as adding/removing <span> tags
        Cursor.setCurrentCursorPosition(offset, richText);
        richText.focus();
      })
    }
  }

  submitSmartInput() {
    const partial = <Partial<Transaction>>this._composingTxn;
    if (partial.payee) {
      const account= this.accountFrequencyTable[partial.payee?.payeeId];
      partial.accountId = account.accountId;
      partial.accountName = account.name;
      partial.currency = account.currency;
      partial.category = this.categoryFrequencyTable[partial.payee?.payeeId];
      partial.date = DateTime.now();
      this.smartInput.emit(new Transaction(partial));
    }
  }
}

// Credit to Liam (Stack Overflow)
// https://stackoverflow.com/a/41034697/3480193

class Cursor {
  // @ts-ignore
  static getCurrentCursorPosition(parentElement) {
    var selection = window.getSelection(),
      charCount = -1,
      node;
    // @ts-ignore
    if (selection.focusNode) {
      // @ts-ignore
      if (Cursor._isChildOf(selection.focusNode, parentElement)) {
        // @ts-ignore
        node = selection.focusNode;
        // @ts-ignore
        charCount = selection.focusOffset;

        while (node) {
          if (node === parentElement) {
            break;
          }

          if (node.previousSibling) {
            node = node.previousSibling;
            // @ts-ignore
            charCount += node.textContent.length;
          } else {
            node = node.parentNode;
            if (node === null) {
              break;
            }
          }
        }
      }
    }

    return charCount;
  }

  // @ts-ignore
  static setCurrentCursorPosition(chars, element) {
    if (chars >= 0) {
      var selection = window.getSelection();
      // @ts-ignore
      let range = Cursor._createRange(element, { count: chars });

      if (range) {
        range.collapse(false);
        // @ts-ignore
        selection.removeAllRanges();
        // @ts-ignore
        selection.addRange(range);
      }
    }
  }

  // @ts-ignore
  static _createRange(node, chars, range) {
    if (!range) {
      range = document.createRange()
      range.selectNode(node);
      range.setStart(node, 0);
    }

    if (chars.count === 0) {
      range.setEnd(node, chars.count);
    } else if (node && chars.count > 0) {
      if (node.nodeType === Node.TEXT_NODE) {
        if (node.textContent.length < chars.count) {
          chars.count -= node.textContent.length;
        } else {
          range.setEnd(node, chars.count);
          chars.count = 0;
        }
      } else {
        for (var lp = 0; lp < node.childNodes.length; lp++) {
          range = Cursor._createRange(node.childNodes[lp], chars, range);

          if (chars.count === 0) {
            break;
          }
        }
      }
    }

    return range;
  }

  // @ts-ignore
  static _isChildOf(node, parentElement) {
    while (node !== null) {
      if (node === parentElement) {
        return true;
      }
      node = node.parentNode;
    }

    return false;
  }
}
