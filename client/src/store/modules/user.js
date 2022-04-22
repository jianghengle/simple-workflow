// initial state
export const state = {
  token: localStorage.getItem('token'),
  email: localStorage.getItem('email'),
  orgIds: null,
}
 
// mutations
export const mutations = {
  setUser (state, user) {
    state.email = user.email
    state.orgIds = user.orgIds
    if (user.token) {
      state.token = user.token
    }
  },


  reset (state) {
    state.token = null
    state.email = null
    state.orgIds = null
    localStorage.removeItem('token')
    localStorage.removeItem('email')
  }
}

export default {
  namespaced: true,
  state,
  mutations
}
