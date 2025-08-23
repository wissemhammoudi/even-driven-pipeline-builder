
import React, { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  PlusIcon,
  CogIcon,
  UserIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UsersIcon
} from '@heroicons/react/24/outline'
import useAuthStore from '../../../store/authStore'
import logo from '../../../assets/logo.svg'

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const location = useLocation()
  const { user, logout, isAdmin } = useAuthStore()  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    ...(isAdmin()
      ? [{ name: 'Create Pipeline', href: '/create-pipeline', icon: PlusIcon }]
      : []),
    {
      name: 'Pipeline Management',
      href: '/pipeline-management',
      icon: ChartBarIcon
    },
    { name: 'Supported Connectors', href: '/config-management', icon: CogIcon },
    ...(isAdmin()
      ? [{ name: 'User Management', href: '/user-management', icon: UsersIcon }]
      : []),
    { name: 'Profile', href: '/profile', icon: UserIcon }
  ]

  const handleLogout = () => {
    logout()
  }

  const isActive = href => {
    return location.pathname === href
  }

  return (
    <>
      {!isOpen && (
        <div className='lg:hidden fixed top-4 left-4 z-50'>
          <button
            onClick={() => setIsOpen(true)}
            className='inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 bg-white shadow-md'
          >
            <span className='sr-only'>Open main menu</span>
            <Bars3Icon className='block h-6 w-6' />
          </button>
        </div>
      )}

      {isOpen && (
        <div className='lg:hidden fixed top-4 left-64 z-50'>
          <button
            onClick={() => setIsOpen(false)}
            className='inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 bg-white shadow-md'
          >
            <span className='sr-only'>Close main menu</span>
            <XMarkIcon className='block h-6 w-6' />
          </button>
        </div>
      )}

      <div className='hidden lg:flex lg:flex-shrink-0'>
        <div
          className={`flex flex-col transition-all duration-300 ease-in-out ${
            isCollapsed ? 'w-16' : 'w-64'
          }`}
        >
          <div className='flex flex-col h-0 flex-1 bg-white border-r border-gray-200 relative'>
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className='absolute -right-3 top-6 bg-white border border-gray-200 rounded-full p-1 shadow-md hover:shadow-lg transition-shadow duration-200 z-10'
            >
              {isCollapsed ? (
                <ChevronRightIcon className='h-4 w-4 text-gray-600' />
              ) : (
                <ChevronLeftIcon className='h-4 w-4 text-gray-600' />
              )}
            </button>

            <div className='flex-1 flex flex-col pt-5 pb-4 overflow-y-auto'>
              <div className='flex flex-col items-center py-6'>
                {!isCollapsed ? (
                  <img src={logo} alt='Logo' style={{ height: 48 }} />
                ) : (
                  <div className='h-8 w-8 bg-primary rounded-lg flex items-center justify-center'>
                    <span className='text-white font-bold text-sm'>D</span>
                  </div>
                )}
              </div>
              <nav className='mt-5 flex-1 px-2 space-y-1'>
                {navigation.map(item => (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                      isActive(item.href)
                        ? 'bg-primary text-white shadow-md'
                        : 'text-gray-600 hover:bg-blue-50 hover:text-primary'
                    }`}
                    title={isCollapsed ? item.name : ''}
                  >
                    <item.icon
                      className={`flex-shrink-0 h-6 w-6 ${
                        isActive(item.href)
                          ? 'text-white'
                          : 'text-gray-500 group-hover:text-primary'
                      } ${!isCollapsed ? 'mr-3' : ''}`}
                    />
                    {!isCollapsed && item.name}
                  </NavLink>
                ))}
              </nav>
            </div>
            <div className='flex-shrink-0 flex bg-gray-50 p-4 border-t border-gray-200'>
              <div className='flex items-center'>
                <div>
                  <div className='h-8 w-8 rounded-full bg-primary flex items-center justify-center'>
                    <span className='text-sm font-medium text-white'>
                      {user?.username?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                </div>
                {!isCollapsed && (
                  <div className='ml-3'>
                    <p className='text-sm font-medium text-black'>
                      {user?.username || 'User'}
                    </p>
                    {isAdmin() && (
                      <span className='text-xs text-blue-600 font-medium'>Admin</span>
                    )}
                    <button
                      onClick={handleLogout}
                      className='text-xs font-medium text-gray-600 hover:text-primary block mt-1'
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className='lg:hidden'>
          <div className='fixed inset-0 flex z-40'>
            <div
              className='fixed inset-0 bg-primary-600 bg-opacity-75'
              onClick={() => setIsOpen(false)}
            ></div>
            <div className='relative flex-1 flex flex-col max-w-xs w-full bg-white'>
              <div className='flex-1 h-0 pt-5 pb-4 overflow-y-auto'>
                <div className='flex-shrink-0 flex items-center px-4'>
                  <h1 className='text-xl font-bold text-gray-900'>
                    Data Pipeline
                  </h1>
                </div>
                <nav className='mt-5 px-2 space-y-1'>
                  {navigation.map(item => (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors duration-200 ${
                        isActive(item.href)
                          ? 'bg-primary text-white shadow-md'
                          : 'text-gray-600 hover:bg-blue-50 hover:text-primary'
                      }`}
                    >
                      <item.icon
                        className={`mr-4 flex-shrink-0 h-6 w-6 ${
                          isActive(item.href)
                            ? 'text-white'
                            : 'text-gray-500 group-hover:text-primary'
                        }`}
                      />
                      {item.name}
                    </NavLink>
                  ))}
                </nav>
              </div>
              <div className='flex-shrink-0 flex bg-gray-50 p-4 border-t border-gray-200'>
                <div className='flex items-center'>
                  <div>
                    <div className='h-8 w-8 rounded-full bg-primary flex items-center justify-center'>
                      <span className='text-sm font-medium text-white'>
                        {user?.username?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                  </div>
                  <div className='ml-3'>
                    <p className='text-base font-medium text-black'>
                      {user?.username || 'User'}
                    </p>
                    {isAdmin() && (
                      <span className='text-sm text-blue-600 font-medium'>Admin</span>
                    )}
                    <button
                      onClick={handleLogout}
                      className='text-sm font-medium text-gray-600 hover:text-primary'
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div className='flex-shrink-0 w-14'></div>
          </div>
        </div>
      )}
    </>
  )
}

export default Sidebar