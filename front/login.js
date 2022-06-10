import { BaseComponent } from './base-component.js'
import decodeJwt from './node_modules/jwt-decode/build/jwt-decode.esm.js'

class KLogin extends BaseComponent {
  constructor () {
    super()
    this.state = {

    }
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
          <kor-input type="text" label="Username"></kor-input>
          <kor-input type="password" label="Password"></kor-input>
          <kor-button label="Sign in" b-listener="click.login"></kor-button>
        </kor-card>
      </div>
      `
  }

  async login () {
    const username = this.shadowRoot.querySelector('[label="Username"]').value
    const passwd = this.shadowRoot.querySelector('[label="Password"]').value

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
