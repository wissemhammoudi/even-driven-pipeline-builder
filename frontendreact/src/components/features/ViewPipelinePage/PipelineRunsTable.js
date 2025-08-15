import React, { useState } from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import { calculateDuration } from '../../../utils/formatters'

const PipelineRunsTable = ({ pipelineRuns }) => {
  const [currentPage, setCurrentPage] = useState(1)
  const runsPerPage = 5

  const getStatusColor = status => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-100 text-green-800'
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const sortedRuns = [...pipelineRuns].sort(
    (a, b) => new Date(b.start_time) - new Date(a.start_time)
  )

  const indexOfLastRun = currentPage * runsPerPage
  const indexOfFirstRun = indexOfLastRun - runsPerPage
  const currentRuns = sortedRuns.slice(indexOfFirstRun, indexOfLastRun)
  const totalPages = Math.ceil(sortedRuns.length / runsPerPage)

  const handlePageChange = page => {
    setCurrentPage(page)
  }

  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <h2 className='text-lg font-medium text-gray-900 mb-4'>Pipeline Runs</h2>
      {pipelineRuns.length === 0 ? (
        <p className='text-gray-500'>No pipeline runs found.</p>
      ) : (
        <>
          <div className='overflow-x-auto'>
            <table className='min-w-full divide-y divide-gray-200'>
              <thead className='bg-gray-50'>
                <tr>
                  <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                    Pipeline Run
                  </th>
                  <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                    Status
                  </th>
                  <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody className='bg-white divide-y divide-gray-200'>
                {currentRuns.map((run, index) => (
                  <tr key={run.run_id}>
                    <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                      #{indexOfFirstRun + index + 1}
                    </td>
                    <td className='px-6 py-4 whitespace-nowrap'>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          run.status
                        )}`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                      {calculateDuration(run.start_time, run.end_time)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className='flex items-center justify-between mt-6'>
              <div className='text-sm text-gray-700'>
                Showing {indexOfFirstRun + 1} to{' '}
                {Math.min(indexOfLastRun, sortedRuns.length)} of{' '}
                {sortedRuns.length} runs
              </div>
              <div className='flex items-center space-x-2'>
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className='inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed'
                >
                  <ChevronLeftIcon className='h-4 w-4' />
                  Previous
                </button>

                <div className='flex items-center space-x-1'>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    page => (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
                          currentPage === page
                            ? 'border-primary-500 text-primary-600 bg-primary-50'
                            : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                        } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                      >
                        {page}
                      </button>
                    )
                  )}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className='inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed'
                >
                  Next
                  <ChevronRightIcon className='h-4 w-4' />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default PipelineRunsTable
