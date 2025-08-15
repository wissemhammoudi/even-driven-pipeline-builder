import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { userPipelineAccessAPI, userAPI } from '../../../../utils/api'

export function usePipelineAccessManagement(pipelineId, currentUserId) {
  const [users, setUsers] = useState([])
  const [nonAdminUsers, setNonAdminUsers] = useState([])
  const [usersWithAccess, setUsersWithAccess] = useState([])
  const [loading, setLoading] = useState(true)
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [selectedUsers, setSelectedUsers] = useState([])
  const [bulkGrantType, setBulkGrantType] = useState('VIEW')
  const [editingAccess, setEditingAccess] = useState(null)
  const [editGrantType, setEditGrantType] = useState('VIEW')
  const [accessDenied, setAccessDenied] = useState(false)
  const [isBulkGranting, setIsBulkGranting] = useState(false)
  const [pendingRevokeUserId, setPendingRevokeUserId] = useState(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      let allUsers = []
      try {
        const response = await userAPI.getUsers()
        allUsers = response.data
      } catch (error) {
        allUsers = []
      }
      const filteredNonAdminUsers = allUsers.filter(user => user.role !== 'admin')
      let usersWithPipelineAccess = []
      try {
        const response = await userPipelineAccessAPI.getUsersForPipeline(pipelineId, currentUserId)
        usersWithPipelineAccess = response.data
      } catch (error) {
        usersWithPipelineAccess = []
      }
      setUsers(allUsers)
      setNonAdminUsers(filteredNonAdminUsers)
      setUsersWithAccess(usersWithPipelineAccess)
    } catch (error) {
      toast.error('Failed to load access data')
    } finally {
      setLoading(false)
    }
  }, [pipelineId, currentUserId])

  useEffect(() => {
    if (pipelineId) {
      loadData()
    }
  }, [pipelineId, loadData])

  const handleBulkGrantAccess = async () => {
    if (selectedUsers.length === 0) {
      toast.error('Please select at least one user')
      return
    }
    setIsBulkGranting(true)
    const requestData = {
      pipeline_id: parseInt(pipelineId),
      user_ids: selectedUsers.map(id => parseInt(id)),
      grant_type: bulkGrantType,
      granted_by: parseInt(currentUserId)
    }
    try {
      await userPipelineAccessAPI.bulkGrantAccess(requestData, currentUserId)
      toast.success(`Access granted to ${selectedUsers.length} users`)
      setShowBulkModal(false)
      setSelectedUsers([])
      setBulkGrantType('VIEW')
      loadData()
    } catch (error) {
      if (error.status === 403) {
        toast.error('Only pipeline owners can manage access')
      } else {
        toast.error(`Failed to grant access to some users: ${error.message}`)
      }
    } finally {
      setIsBulkGranting(false)
    }
  }

  const handleRevokeAccess = userId => {
    setPendingRevokeUserId(userId)
  }

  const confirmRevokeAccess = async () => {
    if (!pendingRevokeUserId) return
    try {
      const requestData = {
        pipeline_id: parseInt(pipelineId),
        user_ids: [parseInt(pendingRevokeUserId)],
        granted_by: parseInt(currentUserId)
      }
      await userPipelineAccessAPI.bulkRevokeAccess(requestData, currentUserId)
      toast.success('Access revoked successfully')
      loadData()
    } catch (error) {
      if (error.status === 403) {
        toast.error('Only pipeline owners can manage access')
      } else {
        toast.error('Failed to revoke access')
      }
    } finally {
      setPendingRevokeUserId(null)
    }
  }

  const handleStartEdit = (accessId, grantType) => {
    setEditingAccess(accessId)
    setEditGrantType(grantType)
  }

  const handleSaveEdit = async (userId) => {
    try {
      await userPipelineAccessAPI.updateAccess(
        {
          user_id: userId,
          pipeline_id: pipelineId,
          grant_type: editGrantType,
          granted_by: currentUserId
        },
        currentUserId
      )
      toast.success('Access updated successfully')
      setEditingAccess(null)
      loadData()
    } catch (error) {
      if (error.status === 403) {
        toast.error('Only pipeline owners can manage access')
      } else {
        toast.error('Failed to update access')
      }
    }
  }

  const handleCancelEdit = () => {
    setEditingAccess(null)
    setEditGrantType('VIEW')
  }

  const getUserById = userId => {
    return users.find(user => user.user_id === userId)
  }

  const userIdsWithAccess = usersWithAccess.map(user => user.user_id)
  const availableUsers = nonAdminUsers.filter(
    user => !userIdsWithAccess.includes(user.user_id)
  )

  return {
    users,
    nonAdminUsers,
    usersWithAccess,
    loading,
    showBulkModal,
    setShowBulkModal,
    selectedUsers,
    setSelectedUsers,
    bulkGrantType,
    setBulkGrantType,
    editingAccess,
    setEditingAccess,
    editGrantType,
    setEditGrantType,
    accessDenied,
    isBulkGranting,
    pendingRevokeUserId,
    setPendingRevokeUserId,
    handleBulkGrantAccess,
    handleRevokeAccess,
    confirmRevokeAccess,
    handleStartEdit,
    handleSaveEdit,
    handleCancelEdit,
    getUserById,
    availableUsers
  }
} 