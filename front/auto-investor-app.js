import { BaseComponent } from './base-component.js'
// import decodeJwt from './node_modules/jwt-decode/build/jwt-decode.js'

const homePage = 'Home Page'
const loginPage = '<k-login b-listener="loginResult.result"></k-login>'
const addStrategyPage = 'Add Strategy Page'

const routes = {
  '#/': homePage,
  '#/login': loginPage,
  '#/add-strategy': addStrategyPage
}

const defaultRoute = '#/'

class AutoInvestorApp extends BaseComponent {
  constructor () {
    super()
    this.state = {
      account: 'logged_out',
      path: '/#/'
    }
  }

  connectedCallback () {
    super.connectedCallback()
    this.validateSession()
    this.setupNavigationHandling()
    window.history.pushState(null, null, defaultRoute)
  }

  setupNavigationHandling () {
    window.onhashchange = ev => {
      const url = ev.newURL.replace('https://', '').replace('http://', '')
      const hashPath = url.substring(url.indexOf('/') + 1)
      this.shadowRoot.querySelector('#page-slot').innerHTML = routes[hashPath]
    }
  }

  validateSession () {
    window.fetch('/api/validate', {
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        Authorization: `Bearer ${window.sessionStorage.getItem('t')}`
      }
    }).then(res => {
      if (res.status >= 200 && res.status <= 209) {
        /* const decodedJwt = decodeJwt(window.sessionStorage.getItem('t'))
        console.log('Decoded JWT:', decodedJwt) */
      }
    })
    // this.addEventListener('loginresult', e => console.log('Login result:', e))
  }

  get css () {
    return `
      .app-bar-nav {
        display: flex;
        justify-content: space-evenly;
        width: 100%;
      }
      .app-bar-nav > a {
        text-decoration: none;
      }
    `
  }

  get html () {
    return `
        <kor-app-bar
          slot="top"
          logo="https://www.svgrepo.com/show/344884/graph-up.svg"
          label="Auto Investor"
        >
          ${this.state.account}
          <div class="app-bar-nav">
            <a href="#/" nav-link><kor-text size="header-1" color="blue">Home</kor-text></a>
            <a href="#/login" nav-link><kor-text size="header-1" color="blue">Login</kor-text></a>
            <a href="#/add-strategy" nav-link><kor-text size="header-1" color="blue">Add Strategy</kor-text></a>
          </div>
        </kor-app-bar>
        <div id="page-slot">${routes[defaultRoute]}</div>
      `
  }

  result (e) {
    console.log('loginResult:', e)
  }
}

window.customElements.define('auto-investor-app', AutoInvestorApp)
