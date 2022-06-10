export class BaseComponent extends window.HTMLElement {
  constructor () {
    super()
    this.attachShadow({ mode: 'open' })
    this.listenerStore = []
  }

  connectedCallback () {
    this.updateTemplate()
    this.update()
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

  updateTemplate () {
    // this.removeEventListeners()
    this.shadowRoot.innerHTML = `
      <style>${this.css}</style>
      ${this.html}`
    this.update()
  }

  update () {
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

  publish (evName, data) {
    const evConfig = {
      detail: data,
      bubbles: true,
      composed: true
    }
    this.dispatchEvent(new window.CustomEvent(evName, evConfig))
  }
}
