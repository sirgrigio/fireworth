import { Component, ContentChild, Input, OnInit, TemplateRef } from '@angular/core';

type CellAlignment = 'start' | 'center' | 'end' | 'between';

@Component({
  selector: 'app-cell',
  templateUrl: './cell.component.html',
  styleUrls: ['./cell.component.scss']
})
export class CellComponent implements OnInit {

  @Input() value: string = '';
  @Input() prefix: string = '';
  @Input() suffix: string = '';
  @Input() alignment: CellAlignment = 'between';
  @Input() textColor: string | null = null;
  @Input() bgColor: string | null = null;

  @ContentChild('prefix') prefix_view: TemplateRef<any> | null = null;
  @ContentChild('suffix') suffix_view: TemplateRef<any> | null = null;

  constructor() { }

  ngOnInit(): void {
  }

}
