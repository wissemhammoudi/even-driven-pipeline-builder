import { useEffect, useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import useAuthStore from '../../store/authStore';
import usePipelineStore from '../../store/pipelineStore';
import userPipelineAccessAPI from '../../api/userPipelineAccessApi';

const buildPipelineFilters = ({ showDeprecated, page, pageSize, searchTerm, dateFilter }) => ({
  deprecated: showDeprecated,
  page: page,
  page_size: pageSize,
  name: searchTerm || undefined,
  created_date: dateFilter || undefined
});

const usePipelineManagementPage = () => {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuthStore();
  const {
    pipelines = [],
    fetchPipelines,
    deletePipeline,
    isLoading,
    error,
    totalCount = 0
  } = usePipelineStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [showDeprecated, setShowDeprecated] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [actionLoading, setActionLoading] = useState({});
  const [pipelinePermissions, setPipelinePermissions] = useState({});
  const [permissionsLoading, setPermissionsLoading] = useState(false);

  const filters = useMemo(() => buildPipelineFilters({
    showDeprecated,
    page: currentPage,
    pageSize,
    searchTerm,
    dateFilter
  }), [showDeprecated, currentPage, pageSize, searchTerm, dateFilter]);

  useEffect(() => {
    if (user?.user_id) {
      fetchPipelines(user.user_id, filters);
    }
  }, [user?.user_id, fetchPipelines, filters]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, dateFilter, showDeprecated]);

  const paginatedResult = useMemo(() => ({
    items: pipelines,
    pagination: {
      currentPage: currentPage,
      totalPages: Math.ceil(totalCount / pageSize),
      pageSize: pageSize,
      totalItems: totalCount
    }
  }), [pipelines, currentPage, totalCount, pageSize]);

  const handlePageChange = useCallback((page) => {
    setCurrentPage(page);
  }, []);

  const handleClearFilters = useCallback(() => {
    setSearchTerm('');
    setDateFilter('');
    setShowDeprecated(false);
  }, []);

  const handleDeletePipeline = useCallback(async (pipelineId, pipelineName) => {
    setActionLoading(prev => ({ ...prev, [pipelineId]: true }));
    try {
      const result = await deletePipeline(pipelineId);
      if (result.success) {
        await fetchPipelines(user.user_id, filters);
        toast.success(`Pipeline "${pipelineName}" deleted successfully!`);
      }
    } catch (error) {
      toast.error('Failed to delete pipeline');
    } finally {
      setActionLoading(prev => ({ ...prev, [pipelineId]: false }));
    }
  }, [deletePipeline, fetchPipelines, user?.user_id, filters]);

  const handleViewPipeline = useCallback((pipelineId) => {
    navigate(`/view-pipeline/${pipelineId}`);
  }, [navigate]);

  const handleCreatePipeline = useCallback(() => {
    navigate('/create-pipeline');
  }, [navigate]);

  const handleRetry = useCallback(() => {
    if (user?.user_id) {
      fetchPipelines(user.user_id, filters);
    }
  }, [user?.user_id, fetchPipelines, filters]);

  const hasPermission = useCallback((pipelineId, permissionType) => {
    if (isAdmin()) return true;
    if (permissionsLoading) return false;
    const permissions = pipelinePermissions[pipelineId];
    if (!permissions) return false;
    return permissions[permissionType] || false;
  }, [isAdmin, permissionsLoading, pipelinePermissions]);

  const fetchPipelinePermissions = useCallback(async () => {
    if (!user?.user_id || !pipelines.length) return;
    if (isAdmin()) {
      setPermissionsLoading(false);
      return;
    }
    setPermissionsLoading(true);
    const permissions = {};
    const activePipelines = pipelines.filter(pipeline => !pipeline.is_deprecated);
    for (const pipeline of activePipelines) {
      try {
        const data = await userPipelineAccessAPI.getUserPermissions(
          pipeline.pipeline_id,
          user.user_id
        );
        permissions[pipeline.pipeline_id] = data;
      } catch (error) {
        permissions[pipeline.pipeline_id] = {
          can_view_pipeline: true,
          can_start_pipeline: true,
          can_start_visualization: true,
          can_manage_access: false,
          can_edit_pipeline: false,
          can_delete_pipeline: false
        };
      }
    }
    setPipelinePermissions(permissions);
    setPermissionsLoading(false);
  }, [user?.user_id, pipelines, isAdmin]);

  useEffect(() => {
    fetchPipelinePermissions();
  }, [pipelines, user?.user_id, fetchPipelinePermissions]);

  return {
    searchTerm,
    setSearchTerm,
    dateFilter,
    setDateFilter,
    showDeprecated,
    setShowDeprecated,
    paginatedResult,
    isLoading,
    isAdmin,
    handleCreatePipeline,
    handleViewPipeline,
    handleDeletePipeline,
    handlePageChange,
    handleClearFilters,
    hasPermission,
    actionLoading,
    permissionsLoading
  };
};

export default usePipelineManagementPage; 