import { BaseComponent, baseUrl } from './base-component.js'
import decodeJwt from 'jwt-decode/build/jwt-decode.esm.js'

const homePage = '<home-page></home-page>'
const loginPage = '<login-page></login-page>'
const addStrategyPage = '<add-strategy-page></add-strategy-page>'

const routes = {
  '#/': homePage,
  '#/login': loginPage,
  '#/add-strategy': addStrategyPage
}

const defaultRoute = '#/'

const investorAppBarBtns = `
  <a href="#/" nav-link><kor-text size="header-1" color="blue">Home</kor-text></a>
  <a href="#/login" nav-link><kor-text size="header-1" color="blue">Log out</kor-text></a>`
const adminAppBarBtns = `
  <a href="#/" nav-link><kor-text size="header-1" color="blue">Home</kor-text></a>
  <a href="#/add-strategy" nav-link><kor-text size="header-1" color="blue">Add Strategy</kor-text></a>
  <a href="#/login" nav-link><kor-text size="header-1" color="blue">Log out</kor-text></a>`

class AutoInvesting extends BaseComponent {
  constructor() {
    super()
    this.gotLoginResult = this.gotLoginResult.bind(this)
    this.onHashChange = this.onHashChange.bind(this)
    this.endSession = this.endSession.bind(this)
  }

  connectedCallback() {
    super.connectedCallback()
    this.validateSession()
    this.addEventListener('loginResult', e => this.gotLoginResult(e.detail))
    this.addEventListener('endSession', this.endSession)
    window.onhashchange = this.onHashChange
  }

  disconnectedCallback() {
    super.disconnectedCallback()
    this.removeEventListener('loginResult', e => this.gotLoginResult(e.detail))
    this.removeEventListener('endSession', this.endSession)
  }

  gotLoginResult(accountType) {
    const appBarBtns = {
      investor: investorAppBarBtns,
      admin: adminAppBarBtns
    }[accountType] || ''
    const isAuthenticated = (accountType === 'investor' || accountType === 'admin')
    const hashGoTo = isAuthenticated
      ? '#/'
      : '#/login'
    this.navigateToHash(hashGoTo)
    this.shadowRoot.querySelector('.app-bar-nav').innerHTML = appBarBtns
    this.shadowRoot.querySelector('#page-slot').innerHTML = routes[hashGoTo]
    this.shadowRoot.querySelector('#accountTypeStatus').innerHTML = accountType
    window.AUTOINVESTING.user.accountType = accountType
  }

  endSession() {
    this.shadowRoot.querySelector('.app-bar-nav').innerHTML = ''
    this.shadowRoot.querySelector('#accountTypeStatus').innerHTML = 'logged_out'
    window.sessionStorage.removeItem('t')
    window.AUTOINVESTING.user.accountType = 'logged_out'
  }

  setupNavigationHandling() {
    window.history.pushState(null, null, defaultRoute)
  }

  onHashChange(e) {
    if (window.AUTOINVESTING.user.accountType === 'logged_out') {
      if (window.location.hash !== '#/login') {
        const hashPath = '#/login'
        this.navigateToHash(hashPath)
        this.shadowRoot.querySelector('#page-slot').innerHTML = routes[hashPath]
      }
    } else {
      const url = e.newURL.replace('https://', '').replace('http://', '')
      const hashPath = url.substring(url.indexOf('/') + 1)
      this.shadowRoot.querySelector('#page-slot').innerHTML = routes[hashPath]
    }
  }

  validateSession() {
    window.fetch(baseUrl + '/api/validate', {
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        Authorization: `Bearer ${window.sessionStorage.getItem('t')}`
      }
    }).then(res => {
      if (res.status >= 200 && res.status <= 209) {
        const decodedJwt = decodeJwt(window.sessionStorage.getItem('t'))
        window.AUTOINVESTING.user = decodedJwt
        const accountType = decodedJwt.accountType
        this.gotLoginResult(accountType)
      } else {
        window.AUTOINVESTING.user.accountType = 'logged_out'
        this.gotLoginResult('logged_out')
      }
    })
  }

  get css() {
    return `
      .app-bar-nav {
        display: flex;
        justify-content: space-evenly;
        width: 100%;
      }
      .app-bar-nav > a {
        text-decoration: none;
      }
      .page-slot {
        overflow: scroll;
        height: 100%;
      }
    `
  }

  get html() {
    return `
        <kor-app-bar
          slot="top"
          logo="https://www.svgrepo.com/show/344884/graph-up.svg"
          label="Auto Investing"
          b-innerhtml="account"
        >
          <div class="app-bar-nav"></div>
          <div id="accountTypeStatus">logged_out</div>
        </kor-app-bar>
        <div id="page-slot" class="page-slot">${routes[defaultRoute]}</div>
      `
  }
}

window.customElements.define('auto-investing', AutoInvesting)
