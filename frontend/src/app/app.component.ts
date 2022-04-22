import { Component, OnInit } from '@angular/core';
import { faBookOpen, faChartBar, faChartLine, faColumns, faCreditCard } from '@fortawesome/free-solid-svg-icons';

import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  navbarCollapsed: boolean = false;
  faBookOpen = faBookOpen;
  faChartBar = faChartBar;
  faChartLine = faChartLine;
  faCreditCard = faCreditCard;
  faTableColumns = faColumns;

  constructor(private translate: TranslateService) { }

  ngOnInit(): void {
    this.translate.addLangs(["en", "it"]);
    this.translate.setDefaultLang(this.translate.langs[0]);
  }

  updateLanguage(event: any): void {
    this.translate.use(event.target.value);
  }
}
