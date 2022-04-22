import { Component, Input, OnInit } from '@angular/core';
import { faAngleDown, faAngleUp } from '@fortawesome/free-solid-svg-icons';
import { StatementSection } from '../../statements.models';

@Component({
  selector: 'app-statement-section',
  templateUrl: './statement-section.component.html',
  styleUrls: ['./statement-section.component.scss']
})
export class StatementSectionComponent implements OnInit {

  @Input() section: StatementSection | null = null;
  @Input() isCollapsed: boolean = false;
  @Input() accentTextColor: string | null = null;

  @Input() _recursive: boolean = false;

  faAngleUp = faAngleUp;
  faAngleDown = faAngleDown;

  constructor() { }

  ngOnInit(): void {
  }

}
