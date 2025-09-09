import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'qa-public-api',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './public-api.component.html',
  styleUrls: ['./public-api.component.scss']
})
export class PublicApiComponent {

  copy(id: string) {
    const el = document.getElementById(id) as HTMLTextAreaElement | null;
    if (!el) return;
    el.select();
    el.setSelectionRange(0, el.value.length);
    navigator.clipboard?.writeText(el.value);
  }

}
