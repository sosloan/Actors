import React, { useState, useEffect } from 'react';

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  color: string;
  component: string;
  description: string;
  badge?: string;
  badgeColor?: string;
}

interface UserProfile {
  name: string;
  avatar: string;
  role: string;
  notifications: number;
  lastLogin: string;
}

const ACTORSNavigation: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [userProfile] = useState<UserProfile>({
    name: 'Alex Johnson',
    avatar: '👤',
    role: 'Financial Analyst',
    notifications: 7,
    lastLogin: '2 minutes ago'
  });

  const navigationItems: NavigationItem[] = [
    {
      id: 'dashboard',
      label: 'Command Center',
      icon: '🏠',
      color: 'from-blue-500 to-blue-700',
      component: 'ACTORS_Dashboard',
      description: 'System overview and real-time monitoring',
      badge: 'Live',
      badgeColor: 'bg-green-500'
    },
    {
      id: 'agents',
      label: 'Agent Network',
      icon: '🤖',
      color: 'from-purple-500 to-purple-700',
      component: 'AgentNetwork',
      description: 'Distributed autonomous agents status',
      badge: '18 Active',
      badgeColor: 'bg-blue-500'
    },
    {
      id: 'trading',
      label: 'Trading Floor',
      icon: '📊',
      color: 'from-green-500 to-green-700',
      component: 'TradingFloor',
      description: 'Real-time trading and portfolio management',
      badge: 'Market Open',
      badgeColor: 'bg-green-500'
    },
    {
      id: 'patterns',
      label: 'Production Patterns',
      icon: '🏭',
      color: 'from-orange-500 to-orange-700',
      component: 'ProductionPatternsDashboard',
      description: 'Circuit breakers, event sourcing, and tracing',
      badge: 'Healthy',
      badgeColor: 'bg-green-500'
    },
    {
      id: 'time',
      label: 'Time Orchestration',
      icon: '⏰',
      color: 'from-cyan-500 to-cyan-700',
      component: 'TimeOrchestrationDashboard',
      description: 'Intelligent scheduling and dependencies',
      badge: '5 Events',
      badgeColor: 'bg-cyan-500'
    },
    {
      id: 'freedom',
      label: 'Financial Freedom',
      icon: '💎',
      color: 'from-pink-500 to-pink-700',
      component: 'FinancialFreedomDashboard',
      description: 'FIRE planning and passive income tracking',
      badge: 'On Track',
      badgeColor: 'bg-pink-500'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: '📈',
      color: 'from-indigo-500 to-indigo-700',
      component: 'Analytics',
      description: 'Advanced analytics and reporting',
      badge: 'Updated',
      badgeColor: 'bg-indigo-500'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      color: 'from-gray-500 to-gray-700',
      component: 'Settings',
      description: 'System configuration and preferences'
    }
  ];

  const filteredNavigationItems = navigationItems.filter(item =>
    item.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleNavigation = (itemId: string) => {
    setActiveSection(itemId);
    setIsMobileMenuOpen(false);
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const renderSidebar = () => (
    <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} border-r ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} min-h-screen transition-all duration-300 ${
      isSidebarCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          {!isSidebarCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🦞</div>
              <div>
                <h1 className="text-lg font-bold text-white">ACTORS</h1>
                <p className="text-xs text-gray-400">v2.1.0</p>
              </div>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="text-white">
              {isSidebarCollapsed ? '→' : '←'}
            </span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      {!isSidebarCollapsed && (
        <div className="p-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span className="absolute right-3 top-2.5 text-gray-400">🔍</span>
          </div>
        </div>
      )}

      {/* Navigation Items */}
      <nav className="p-4 space-y-2">
        {filteredNavigationItems.map(item => (
          <button
            key={item.id}
            onClick={() => handleNavigation(item.id)}
            className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center space-x-3 group ${
              activeSection === item.id
                ? `bg-gradient-to-r ${item.color} text-white shadow-lg`
                : `${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            {!isSidebarCollapsed && (
              <>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{item.label}</span>
                    {item.badge && (
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${item.badgeColor} text-white`}>
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-xs opacity-75 mt-1">{item.description}</p>
                </div>
              </>
            )}
          </button>
        ))}
      </nav>

      {/* User Profile */}
      {!isSidebarCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center text-lg">
              {userProfile.avatar}
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">{userProfile.name}</p>
              <p className="text-xs text-gray-400">{userProfile.role}</p>
            </div>
            <div className="relative">
              <button className="p-2 rounded-lg hover:bg-gray-700 transition-colors">
                <span className="text-white">🔔</span>
                {userProfile.notifications > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs text-white">
                    {userProfile.notifications}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderHeader = () => (
    <header className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} p-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="text-white">☰</span>
          </button>

          {/* Breadcrumb */}
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">🏠</span>
            <span className="text-gray-400">/</span>
            <span className="text-white font-semibold">
              {navigationItems.find(item => item.id === activeSection)?.label || 'Dashboard'}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Search Bar (Desktop) */}
          <div className="hidden md:block relative">
            <input
              type="text"
              placeholder="Search..."
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
            />
            <span className="absolute right-3 top-2.5 text-gray-400">🔍</span>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="text-white">{isDarkMode ? '☀️' : '🌙'}</span>
          </button>

          {/* Notifications */}
          <div className="relative">
            <button className="p-2 rounded-lg hover:bg-gray-700 transition-colors">
              <span className="text-white">🔔</span>
              {userProfile.notifications > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs text-white">
                  {userProfile.notifications}
                </span>
              )}
            </button>
          </div>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-sm">
              {userProfile.avatar}
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-semibold text-white">{userProfile.name}</p>
              <p className="text-xs text-gray-400">{userProfile.role}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );

  const renderMobileMenu = () => (
    isMobileMenuOpen && (
      <div className="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50">
        <div className="fixed left-0 top-0 h-full w-64 bg-gray-800 p-4">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🦞</div>
              <div>
                <h1 className="text-lg font-bold text-white">ACTORS</h1>
                <p className="text-xs text-gray-400">v2.1.0</p>
              </div>
            </div>
            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <span className="text-white">✕</span>
            </button>
          </div>

          <div className="space-y-2">
            {navigationItems.map(item => (
              <button
                key={item.id}
                onClick={() => handleNavigation(item.id)}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center space-x-3 ${
                  activeSection === item.id
                    ? `bg-gradient-to-r ${item.color} text-white shadow-lg`
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{item.label}</span>
                    {item.badge && (
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${item.badgeColor} text-white`}>
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-xs opacity-75 mt-1">{item.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  );

  const renderContent = () => {
    const activeItem = navigationItems.find(item => item.id === activeSection);
    return (
      <div className="flex-1 p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">
            {activeItem?.icon} {activeItem?.label}
          </h1>
          <p className="text-gray-400">{activeItem?.description}</p>
        </div>
        
        <div className="bg-gray-800 rounded-2xl p-6">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">{activeItem?.icon}</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              {activeItem?.label} Component
            </h2>
            <p className="text-gray-400 mb-6">
              This would render the {activeItem?.component} component
            </p>
            <div className="bg-gray-700 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-gray-300">
                <strong>Component:</strong> {activeItem?.component}
              </p>
              <p className="text-sm text-gray-300 mt-2">
                <strong>Status:</strong> Ready to integrate
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
      <div className="flex">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block">
          {renderSidebar()}
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {renderHeader()}
          {renderContent()}
        </div>
      </div>

      {/* Mobile Menu */}
      {renderMobileMenu()}
    </div>
  );
};

export default ACTORSNavigation;
