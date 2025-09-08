# 🎨 ACTORS Frontend Components

*Enhanced React components for the ACTORS distributed autonomous agent system*

## 🚀 Overview

This directory contains modern, production-ready React components for the ACTORS system, featuring beautiful UI/UX design, real-time data visualization, and comprehensive financial trading interfaces.

## 📁 Component Structure

### **🏠 Core Components**

#### **ACTORS_Dashboard.tsx**
- **Main system dashboard** with real-time monitoring
- **System health metrics** and agent status
- **Production patterns monitoring** (Circuit Breakers, Event Sourcing, Distributed Tracing)
- **Market data visualization** with interactive charts
- **Dark/light theme support** and responsive design

#### **FinancialFreedomDashboard.tsx**
- **FIRE planning interface** with goal tracking
- **Passive income streams** monitoring and optimization
- **Net worth projections** with interactive charts
- **Financial goal progress** with visual indicators
- **Action items** for accelerating FIRE timeline

#### **ProductionPatternsDashboard.tsx**
- **Circuit Breaker monitoring** with real-time status
- **Event Store visualization** with recent events
- **Distributed Tracing** with request flow analysis
- **Saga Pattern management** for distributed transactions
- **System health metrics** and performance monitoring

#### **TimeOrchestrationDashboard.tsx**
- **Intelligent scheduling** with dependency management
- **Event dependency graphs** with visual flow
- **Smart scheduling analytics** with ML recommendations
- **Performance metrics** and execution monitoring
- **Real-time event status** updates

#### **ACTORS_Navigation.tsx**
- **Responsive navigation system** with sidebar and mobile support
- **Search functionality** across all components
- **User profile management** with notifications
- **Theme switching** (dark/light mode)
- **Breadcrumb navigation** and component routing

## 🎨 Design Features

### **Visual Design**
- **Modern gradient backgrounds** with brand colors
- **Smooth animations** and transitions
- **Interactive charts** using Recharts library
- **Responsive grid layouts** for all screen sizes
- **Professional typography** with Inter font family

### **Color Scheme**
- **ACTORS Blue**: Primary brand color (#3B82F6)
- **ACTORS Purple**: Secondary accent (#A855F7)
- **ACTORS Green**: Success and positive metrics (#22C55E)
- **ACTORS Orange**: Warnings and attention (#F97316)
- **ACTORS Cyan**: Information and data (#06B6D4)
- **ACTORS Pink**: Financial freedom features (#EC4899)

### **Interactive Elements**
- **Hover effects** on all interactive components
- **Loading states** and skeleton screens
- **Toast notifications** for user feedback
- **Modal dialogs** for detailed information
- **Tooltips** for additional context

## 🛠️ Technical Implementation

### **Technologies Used**
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for utility-first styling
- **Recharts** for data visualization
- **Framer Motion** for animations
- **React Router** for navigation
- **React Query** for data fetching
- **Axios** for HTTP requests

### **Key Features**
- **Real-time data updates** with WebSocket connections
- **Responsive design** for mobile, tablet, and desktop
- **Accessibility support** with ARIA labels and keyboard navigation
- **Performance optimization** with React.memo and useMemo
- **Error boundaries** for graceful error handling
- **Progressive loading** for better user experience

## 📊 Data Visualization

### **Chart Types**
- **Line Charts**: Market data and performance trends
- **Area Charts**: Portfolio value and net worth projections
- **Bar Charts**: Comparative metrics and rankings
- **Pie Charts**: Asset allocation and distribution
- **Radial Charts**: System health and circular metrics

### **Interactive Features**
- **Zoom and pan** on time-series data
- **Tooltip information** on hover
- **Legend toggling** for data series
- **Responsive sizing** for all screen sizes
- **Custom color schemes** for different data types

## 🎯 Component Features

### **Dashboard Components**
- **Real-time metrics** with live updates
- **System status indicators** with color coding
- **Performance charts** with historical data
- **Alert notifications** for important events
- **Quick action buttons** for common tasks

### **Financial Components**
- **Portfolio tracking** with real-time values
- **Goal progress** with visual indicators
- **Risk assessment** with color-coded warnings
- **Performance attribution** with detailed breakdowns
- **Tax optimization** suggestions and tracking

### **Production Components**
- **Circuit breaker status** with failure tracking
- **Event sourcing** with audit trails
- **Distributed tracing** with request flows
- **Saga management** with transaction monitoring
- **System health** with comprehensive metrics

## 🚀 Getting Started

### **Prerequisites**
- Node.js 16+ and npm/yarn
- React development environment
- TypeScript knowledge (recommended)

### **Installation**
```bash
# Navigate to examples directory
cd examples

# Install dependencies
npm install

# Start development server
npm start
```

### **Development Commands**
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

## 🎨 Customization

### **Theming**
- **Dark/Light mode** toggle in navigation
- **Custom color schemes** in Tailwind config
- **Brand colors** for ACTORS system
- **Responsive breakpoints** for all devices

### **Styling**
- **Tailwind CSS** utility classes
- **Custom animations** and transitions
- **Gradient backgrounds** and effects
- **Responsive design** patterns

### **Data Integration**
- **API endpoints** for real-time data
- **WebSocket connections** for live updates
- **Mock data** for development
- **Error handling** for network issues

## 📱 Responsive Design

### **Breakpoints**
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1440px
- **Large Desktop**: 1440px+

### **Mobile Features**
- **Collapsible sidebar** navigation
- **Touch-friendly** interactive elements
- **Optimized charts** for small screens
- **Swipe gestures** for navigation

## 🔧 Configuration

### **Environment Variables**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000/ws
REACT_APP_VERSION=2.1.0
```

### **Tailwind Configuration**
- **Custom colors** for ACTORS brand
- **Extended animations** and keyframes
- **Custom spacing** and sizing
- **Plugin integrations** for forms and typography

## 🧪 Testing

### **Test Coverage**
- **Component rendering** tests
- **User interaction** tests
- **Data visualization** tests
- **Responsive design** tests
- **Accessibility** tests

### **Testing Tools**
- **Jest** for unit testing
- **React Testing Library** for component testing
- **Cypress** for end-to-end testing
- **Storybook** for component documentation

## 📚 Documentation

### **Component Documentation**
- **Props interfaces** with TypeScript
- **Usage examples** for each component
- **Styling guidelines** and best practices
- **Performance considerations** and optimizations

### **API Integration**
- **REST API** endpoints documentation
- **WebSocket** event specifications
- **Data models** and interfaces
- **Error handling** patterns

## 🚀 Deployment

### **Production Build**
```bash
# Build optimized production bundle
npm run build

# Serve static files
npm run serve
```

### **Deployment Options**
- **Static hosting** (Netlify, Vercel, GitHub Pages)
- **Docker containers** for containerized deployment
- **CDN integration** for global distribution
- **Environment-specific** configurations

## 🤝 Contributing

### **Development Guidelines**
- **TypeScript** for type safety
- **ESLint** for code quality
- **Prettier** for code formatting
- **Conventional commits** for version control

### **Component Standards**
- **Functional components** with hooks
- **Props interfaces** with TypeScript
- **Responsive design** for all components
- **Accessibility** compliance (WCAG 2.1)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

*"Beautiful, modern, and functional - the ACTORS frontend brings financial intelligence to life!"* 🎨✨🚀
