import { BaseComponent } from './base-component.js'
import './node_modules/@kor-ui/kor/components/button/index.js'

const MAX_COUNT = 5
const MIN_COUNT = 0

class MyCounter extends BaseComponent {
  constructor () {
    super()
    this.state = {
      count: 0,
      ismax: false,
      ismin: false
    }
  }

  static get html () {
    return `
      <button b-listener="onclick_dec" b-boolattr="hidden_ismin" b-attrval="data-id_count">-</button>
      <span b-innerhtml="count"></span>
      <button b-listener="onclick_inc" b-boolattr="hidden_ismax">+</button>
      <kor-button label="Hello World 2" color="primary"></kor-button>`
  }

  static get css () {
    return `
      span {
        font-size: 200%;
      }

      span {
        width: 4rem;
        display: inline-block;
        text-align: center;
      }

      button {
        width: 4rem;
        height: 4rem;
        border: none;
        border-radius: 10px;
        background-color: seagreen;
        color: white;
      }
      `
  }

  inc () {
    if (this.state.count < MAX_COUNT) {
      ++this.state.count
    }
    this.state.ismax = this.state.count === MAX_COUNT
    this.state.ismin = this.state.count === MIN_COUNT
    this.update()
  }

  dec () {
    if (this.state.count > MIN_COUNT) {
      this.state.count--
    }
    this.state.ismax = this.state.count === MAX_COUNT
    this.state.ismin = this.state.count === MIN_COUNT
    this.update()
  }
}

window.customElements.define('my-counter', MyCounter)
