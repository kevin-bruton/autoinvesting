import { BaseComponent } from '../base-component.js'
import decodeJwt from '../node_modules/jwt-decode/build/jwt-decode.esm.js'

class LoginPage extends BaseComponent {
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
    const usernameInput = this.shadowRoot.querySelector('#username-input')
    const passwordInput = this.shadowRoot.querySelector('#password-input')

    const requestConfig = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ username: usernameInput.value, passwd: passwordInput.value })
    }
    const res = await window.fetch('api/authenticate', requestConfig)
    if (res.status >= 200 && res.status <= 209) {
      const jwt = await res.json()
      window.sessionStorage.setItem('t', jwt.t)
      const decodedJwt = decodeJwt(jwt.t)
      const accountType = decodedJwt.data.accountType
      usernameInput.setAttribute('status', 'success')
      passwordInput.setAttribute('status', 'success')
      setTimeout(() => this.publish('loginResult', accountType), 1000)
    } else {
      // console.log('Auth response error:', res.status, res.statusText)
      usernameInput.setAttribute('status', 'error')
      passwordInput.setAttribute('status', 'error')
    }
  }
}

window.customElements.define('login-page', LoginPage)
