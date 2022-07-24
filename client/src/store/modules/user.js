// initial state
export const state = {
  token: localStorage.getItem('token'),
  email: localStorage.getItem('email'),
  username: localStorage.getItem('username'),
  orgIds: null,
}
 
// mutations
export const mutations = {
  setUser (state, user) {
    state.email = user.email
    state.username = user.username
    state.orgIds = user.orgIds
    if (user.token) {
      state.token = user.token
    }
  },


  reset (state) {
    state.token = null
    state.email = null
    state.username = null
    state.orgIds = null
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    localStorage.removeItem('username')
  },

  addOrgId (state, orgId) {
    if (!state.orgIds) {
      state.orgIds = []
    }
    state.orgIds.push(orgId)
  }
}

export default {
  namespaced: true,
  state,
  mutations
}
