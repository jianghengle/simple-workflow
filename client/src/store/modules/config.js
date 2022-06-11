const dev = process.env.NODE_ENV == 'development'

// initial state
export const state = {
  server: dev ? 'http://localhost:3000' : 'https://uawh1iugaj.execute-api.us-west-2.amazonaws.com/Prod',
  workflowFilter: 'All'
}

// mutations
export const mutations = {
  setWorkflowFilter (state, workflowFilter) {
    state.workflowFilter = workflowFilter
  },
}

export default {
  namespaced: true,
  state,
  mutations
}
