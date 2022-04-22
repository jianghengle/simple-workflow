// initial state
export const state = {
  org: null,
  orgUsers: null,
  orgWorkflowConfigs: null,
}

// mutations
export const mutations = {
  setOrg (state, org) {
    state.org = org
  },

  setOrgUsers (state, orgUsers) {
    state.orgUsers = orgUsers.sort(function(a, b) {
      if (a.role == b.role) {
        return a.email.localeCompare(b.email)
      }
      var roles = ['Owner', 'Admin', 'User']
      return roles.indexOf(a.role) - roles.indexOf(b.role)
    })
  },

  updateOrgUser (state, orgUser) {
    var index = -1
    for(var i=0;i<state.orgUsers.length;i++) {
      if (state.orgUsers[i].email == orgUser.email) {
        index = i
        break
      }
    }
    if (index == -1)  {
      state.orgUsers.push(orgUser)
    } else {
      state.orgUsers.splice(i, 1, orgUser)
    }
  },

  deleteOrgUser (state, email) {
    var index = -1
    for(var i=0;i<state.orgUsers.length;i++) {
      if (state.orgUsers[i].email == email) {
        index = i
        break
      }
    }
    if (index != -1)  {
      state.orgUsers.splice(index, 1)
    }
  },

  setOrgWorkflowConfigs (state, orgWorkflowConfigs) {
    state.orgWorkflowConfigs = orgWorkflowConfigs
  },

  updateOrgWorkflowConfig (state, orgWorkflowConfig) {
    var index = -1
    for(var i=0;i<state.orgWorkflowConfigs.length;i++) {
      if (state.orgWorkflowConfigs[i].id == orgWorkflowConfig.id) {
        index = i
        break
      }
    }
    if (index != -1) {
      state.orgWorkflowConfigs.splice(index, 1, orgWorkflowConfig)
    }
  },

  addOrgWorkflowConfig (state, orgWorkflowConfig) {
    state.orgWorkflowConfigs.push(orgWorkflowConfig)
  },

  removeOrgWorkflowConfig (state, orgWorkflowConfig) {
    var index = -1
    for(var i=0;i<state.orgWorkflowConfigs.length;i++) {
      if (state.orgWorkflowConfigs[i].id == orgWorkflowConfig.id) {
        index = i
        break
      }
    }
    if (index != -1) {
      state.orgWorkflowConfigs.splice(index, 1)
    }
  },
}

export default {
  namespaced: true,
  state,
  mutations
}
