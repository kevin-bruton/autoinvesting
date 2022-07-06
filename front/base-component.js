export const baseUrl = 'http://autoinvesting.local:5000'

export class BaseComponent extends window.HTMLElement {
  constructor () {
    super()
    this.attachShadow({ mode: 'open' })
    this.isHtmlSet = false
  }

  connectedCallback () {
    this.shadowRoot.innerHTML = `
      <style>${this.css}</style>
      ${this.html}`
    this.isHtmlSet = true
  }

  navigateToHash (hash) {
    if (window.location.hash !== hash) {
      window.location.hash = hash
    }
  }

  getEl (id) {
    return this.shadowRoot.getElementById(id)
  }

  getVal (id) {
    return this.shadowRoot?.getElementById(id).value
  }

  getInputFile (id) {
    const files = this.shadowRoot.getElementById(id).files
    return files.length ? files[0] : null
  }

  getInputFilename (id) {
    const files = this.shadowRoot.getElementById(id).files
    return files.length ? files[0].name : null
  }

  async getInputFileContent (id) {
    return new Promise(resolve => {
      const files = this.shadowRoot?.getElementById(id).files
      if (!files.length)
        return null
      const file = files[0]
      const reader = new FileReader()
      reader.addEventListener('load', ev => {
        resolve(ev.target.result)
      }, false)
      reader.readAsText(file);
    })
  }

  setInnerHtml (id, html) {
    this.shadowRoot.getElementById(id).innerHTML = html
  }

  setAttrib (id, attrName, attrVal) {
    this.shadowRoot?.getElementById(id).setAttribute(attrName, attrVal)
  }

  async httpGet (url, params) {
    const searchParams = new URLSearchParams(params).toString()
    const jwt = window.sessionStorage.getItem('t')
    const res = await window.fetch(baseUrl + url + searchParams, { headers: { Authorization: `Bearer ${jwt}` } })
    if (res.status >= 200 && res.status <= 209) {
      const data = await res.json()
      return { ...data, ...{ status: res.status } }
    }
    if (res.status === 401) {
      window.location.assign('#/login')
    }
    return { status: res.status, statusText: res.statusText }
  }

  async httpPost (url, data) {
    const jwt = window.sessionStorage.getItem('t')
    const headers = {
      Authorization: `Bearer ${jwt}`,
      'Content-Type': 'application/json'
    }
    const res = await window.fetch(baseUrl + url, { method: 'POST', headers, body: JSON.stringify(data) })
    if (res.status >= 200 && res.status <= 209) {
      const data = await res.json()
      return { ...data, ...{ status: res.status } }
    }
    if (res.status === 401) {
      window.location.assign('#/login')
    }
    return { status: res.status, statusText: res.statusText }
  }

  async httpPostFile (file, strategyName='', symbol='', environment='') {
    const jwt = window.sessionStorage.getItem('t')
    const formData = new window.FormData()
    strategyName && formData.append('strategyName', strategyName)
    symbol && formData.append('symbol', symbol)
    environment && formData.append('environment', environment)
    formData.append('file', file)
    const res = await window.fetch(baseUrl + '/api/files', { method: 'POST', headers: { Authorization: `Bearer ${jwt}` }, body: formData })
    if (res.status >= 200 && res.status <= 209) {
      const result = res.json()
      return result
    }
    if (res.status === 401) {
      window.location.assign('#/login')
    }
    return { success: false, message: `status: ${res.status} statusText: ${res.statusText}` }
  }

  async httpPostBacktest (file, strategyName, btStart, btEnd, btDeposit) {
    const jwt = window.sessionStorage.getItem('t')
    const formData = new window.FormData()
    formData.append('strategyName', strategyName)
    formData.append('btStart', btStart)
    formData.append('btEnd', btEnd)
    formData.append('btDeposit', btDeposit)
    formData.append('file', file)
    const res = await window.fetch(baseUrl + '/api/backtest', { method: 'POST', headers: { Authorization: `Bearer ${jwt}` }, body: formData })
    if (res.status >= 200 && res.status <= 209) {
      const result = res.json()
      return result
    }
    if (res.status === 401) {
      window.location.assign('#/login')
    }
    return { success: false, message: `status: ${res.status} statusText: ${res.statusText}` }
  }

  publish (evName, data) {
    const evConfig = {
      detail: data,
      bubbles: true,
      composed: true
    }
    this.dispatchEvent(new window.CustomEvent(evName, evConfig))
  }
}
