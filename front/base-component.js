export class BaseComponent extends window.HTMLElement {
  constructor () {
    super()
    this.attachShadow({ mode: 'open' })
    // this.listenerStore = []
  }

  connectedCallback () {
    this.shadowRoot.innerHTML = `
      <style>${this.css}</style>
      ${this.html}`
  }

  navigateToHash (hash) {
    if (window.location.hash !== hash) {
      window.location.hash = hash
    }
  }

  getEl (id) {
    return this.shadowRoot.getElementById(id)
  }

  async httpGet (url, params) {
    const searchParams = new URLSearchParams(params).toString()
    const jwt = window.sessionStorage.getItem('t')
    const res = await window.fetch(url + searchParams, { headers: { Authorization: `Bearer ${jwt}` } })
    if (res.status >= 200 && res.status <= 209) {
      const data = await res.json()
      return { ...data, ...{ status: res.status } }
    }
    return { status: res.status, statusText: res.statusText }
  }

  async httpPost (url, data) {
    const jwt = window.sessionStorage.getItem('t')
    const res = await window.fetch(url, { headers: { Authorization: `Bearer ${jwt}` }, body: JSON.stringify(data) })
    if (res.status >= 200 && res.status <= 209) {
      const data = await res.json()
      return { ...data, ...{ status: res.status } }
    }
    return { status: res.status, statusText: res.statusText }
  }

  async httpPostFile (fileName) {
    const jwt = window.sessionStorage.getItem('t')
    const formData = new window.FormData()
    formData.append('file', fileName)
    const res = await window.fetch('/api/files', { method: 'POST', headers: { Authorization: `Bearer ${jwt}` }, body: formData })
    return { status: res.status, statusText: res.statusText }
  }

  /*   connectedCallback () {
    this.updateTemplate()
  }

  disconnectedCallback () {
    this.removeEventListeners()
  }

  removeEventListeners () {
    this.listenerStore.forEach(l => {
      l.element.removeEventListener(l.eventName, this[l.listener])
    })
    this.listenerStore = []
  }

  setState (node, value) {
    this.state = { ...this.state, ...{ [node]: value } }
    this.updateTemplate()
  }

  updateTemplate () {
    this.removeEventListeners()
    this.shadowRoot.innerHTML = `
      <style>${this.css}</style>
      ${this.html}`
    this.updateBindings()
  }

  updateBindings () {
    console.log('Update bindings. path:', this.state.path)
    // console.log('Update with state:', this.state)
    // apply innerHTML binds
    const textUpdateEls = this.shadowRoot.querySelectorAll('[b-innerhtml]')
    textUpdateEls.forEach(textUpdateEl => {
      textUpdateEl.innerHTML = this.state[textUpdateEl.getAttribute('b-innerhtml')]
    })

    // Apply listeners
    const listenerEls = this.shadowRoot.querySelectorAll('[b-listener]')
    listenerEls.forEach(listenerEl => {
      const [listenerType, listener] = listenerEl.getAttribute('b-listener').split('.')
      // listenerEl[listenerType] = this[listener].bind(this)
      listenerEl.addEventListener(listenerType, this[listener].bind(this))
      this.listenerStore.push({ element: listenerEl, eventName: listenerType, listener })
    })
    const winListenerEls = this.shadowRoot.querySelectorAll('[b-winListener]')
    winListenerEls.forEach(listenerEl => {
      const [listenerType, listener] = listenerEl.getAttribute('b-winListener').split('.')
      // listenerEl[listenerType] = this[listener].bind(this)
      window.addEventListener(listenerType, this[listener].bind(this))
      this.listenerStore.push({ element: window, eventName: listenerType, listener })
    })

    // Apply boolean attribute binds
    const boolAttrEls = this.shadowRoot.querySelectorAll('[b-boolattr]')
    boolAttrEls.forEach(boolAttrEl => {
      const [attrName, stateVarName] = boolAttrEl.getAttribute('b-boolattr').split('.')
      const attrVal = this.state[stateVarName]
      if (attrVal) {
        boolAttrEl.setAttribute(attrName, this.state[stateVarName])
      } else {
        boolAttrEl.removeAttribute(attrName)
      }
    })

    // Apply attribute value binds
    const attrValEls = this.shadowRoot.querySelectorAll('[b-attrval]')
    attrValEls.forEach(attrValEl => {
      const [attrName, stateVarName] = attrValEl.getAttribute('b-attrval').split('.')
      const attrVal = this.state[stateVarName]
      attrValEl.setAttribute(attrName, attrVal)
    })
  }
 */
  publish (evName, data) {
    const evConfig = {
      detail: data,
      bubbles: true,
      composed: true
    }
    this.dispatchEvent(new window.CustomEvent(evName, evConfig))
  }
}
