import { BaseComponent } from './base-component.js'
import decodeJwt from './node_modules/jwt-decode/build/jwt-decode.esm.js'

class KLogin extends BaseComponent {
  constructor () {
    super()
    this.login = this.login.bind(this)
  }

  connectedCallback () {
    super.connectedCallback()
    this.publish('endSession')
    this.shadowRoot.querySelector('#signin-btn').addEventListener('click', this.login)
    // this.publish('loginResult', 'logged_out')
  }

  get css () {
    return `
      .login-page {
        display: grid;
        grid-template-columns: 1fr 300px 1fr;
        grid-template-rows: 1fr 1fr 1fr;
        grid-template-areas:
            ". . ."
            ". login ."
            ". . .";
      }

      .login-box {
        width: 300px;
        grid-area: login;
      }
    `
  }

  get html () {
    return `
      <div class="login-page">
        <kor-card class="login-box" icon="login" label="Login">
          <kor-input type="text" label="Username" id="username-input"></kor-input>
          <kor-input type="password" label="Password" id="password-input"></kor-input>
          <kor-button id="signin-btn" label="Sign in" b-listener="click.login"></kor-button>
        </kor-card>
      </div>
      `
  }

  async login () {
    const username = this.shadowRoot.querySelector('#username-input').value
    const passwd = this.shadowRoot.querySelector('#password-input').value

    console.log('Login. Username:', username, 'Password:', passwd)
    const requestConfig = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ username, passwd })
    }
    const res = await window.fetch('api/authenticate', requestConfig)
    if (res.status >= 200 && res.status <= 209) {
      const jwt = await res.json()
      window.sessionStorage.setItem('t', jwt.t)
      const decodedJwt = decodeJwt(jwt.t)
      console.log('KLogin decodedJwt:', decodedJwt)
      const accountType = decodedJwt.data.accountType
      this.publish('loginResult', accountType)
      // this.dispatchEvent(new window.CustomEvent('loginresult', { detail: accountType, bubbles: true, composed: true}))
    } else {
      console.log('Auth response error:', res.status, res.statusText)
    }
  }
}

window.customElements.define('k-login', KLogin)
