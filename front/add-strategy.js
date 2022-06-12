import { BaseComponent } from './base-component.js'
import getRandomName from './getRandomName.js'

class AddStrategy extends BaseComponent {
  constructor () {
    super()
    this.strategyName = getRandomName()
  }

  connectedCallback () {
    super.connectedCallback()
  }

  get css () {
    return `
      .add-strategy-page {
        display: grid;
        grid-template-columns: 1fr 10fr 1fr;
        grid-template-rows: 1fr 10fr 1fr;
        grid-template-areas:
            ". . ."
            ". addBox ."
            ". . .";
      }

      .add-box {
        grid-area: addBox;
      }
    `
  }

  get html () {
    return `
      <div class="add-strategy-page">
        <kor-card class="add-box" icon="login" label="Addchart">
          <kor-input type="text" label="Strategy Name" id="strategy-name" value="${this.strategyName}"></kor-input>
          <kor-input type="text" label="Symbols that the strategy operates on (separated by commas)" id="symbols"></kor-input>
          <kor-input type="text" label="Timeframes that the strategy operates on (separated by commas)" id="timeframes"></kor-input>
          <kor-input type="text" label="Generated date (format YYYY-MM-DD)" id="generated-date"></kor-input>
          <kor-input type="text" label="Demo date (format YYYY-MM-DD)" id="demo-date"></kor-input>
          <kor-input type="text" label="Live date (format YYYY-MM-DD)" id="live-date"></kor-input>
          <kor-textarea label="Paste MT4 code here" rows="5" value=""></kor-textarea>
          <kor-text size="body-1">SQX strategy file: <input type="file" label="SQX strategy file" id="sqx-strategy-file"></input></kor-text>
          <kor-text size="body-1">SQX trades CSV file: <input type="file" label="SQX strategy file" id="sqx-strategy-file"></input></kor-text>
          <kor-button id="save" label="Save"></kor-button>
        </kor-card>
      </div>
      `
  }
}

window.customElements.define('add-strategy', AddStrategy)
