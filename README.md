# Face Recognition Attendance System

A modern, modular face recognition attendance system built with Python and CustomTkinter.

## 🚀 Quick Start

### Production Mode

```bash
python main.py
```

### Development Mode (with Hot Reload)

```bash
python dev.py
```

## 📁 Project Structure

```
project-oop-recognition-main/
├── main.py              # Production entry point
├── dev.py               # Development server with hot reload
├── test_auth.py         # Authentication system test script
├── app/
│   ├── ui/
│   │   ├── app.py      # Main application class
│   │   ├── pages/      # Application pages
│   │   │   ├── home.py
│   │   │   ├── dashboard.py
│   │   │   ├── students.py
│   │   │   ├── attendance.py
│   │   │   ├── login.py
│   │   │   └── register.py
│   │   ├── components/ # Reusable UI components
│   │   └── widgets/    # Custom widgets
│   ├── services/       # Business logic services
│   │   ├── auth_service.py    # User authentication
│   │   └── json_store.py      # Data storage
│   ├── database/       # Database configuration
│   └── utils/          # Utility functions
├── data/               # User data storage (auto-created)
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
└── run-dev.bat         # Windows development launcher
```

## 🔥 Development Features

- **Hot Reload**: Automatically restarts the app when Python files change
- **State Preservation**: Your current page and app state is preserved during reloads
- **Modular Design**: Clean separation of concerns with pages and components
- **Development Mode**: Special indicators and features when running in dev mode

## 🔐 Authentication System

The application includes a complete authentication system with:

- **User Registration**: Secure user account creation with validation
- **User Login**: Secure authentication with bcrypt password hashing
- **Secure Storage**: JSON-based user data storage with encrypted passwords
- **Session Management**: Development state preservation across reloads

### Testing Authentication

```bash
# Test the authentication system
python test_auth.py
```

This will create test users and demonstrate the authentication functionality.

## 📱 Application Flow

### 1. **Home Page** 🏠

- **Landing page** with system introduction
- **Login/Register buttons** at the top right
- **Feature showcase** and get started section
- **No authentication required** - public access

### 2. **Authentication Pages** 🔐

- **Login Page**: User authentication with username/password
- **Register Page**: New user account creation
- **Back to Home** buttons for easy navigation
- **Automatic redirect** to main app after successful auth

### 3. **Main Application** 📊

After successful login/registration, users access:

- **📊 Dashboard**: System overview with statistics and quick actions
- **👥 Students**: Student management interface
- **📊 Attendance**: Attendance tracking and reporting

Each page includes:

- **Navigation sidebar** with page switching
- **Logout button** to return to home
- **Current page highlighting** in navigation

## 🛠️ Development Workflow

1. **Start Development Server**:

   ```bash
   python dev.py
   ```

2. **Make Changes**: Edit any Python file in the `app/` directory

3. **Auto-Reload**: The app automatically restarts with your changes

4. **State Preservation**: Your current page and app state is maintained

## 📦 Dependencies

### Production

- `customtkinter` - Modern UI framework
- `opencv-python` - Computer vision
- `face-recognition` - Face recognition library
- `bcrypt` - Secure password hashing

### Development

- `watchdog` - File system monitoring for hot reload
- `psutil` - Process management
- `colorama` - Terminal color output

## 🚀 Running the Application

### Production Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Development Mode

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Start development server with hot reload
python dev.py
```

## 🔧 Configuration

The application automatically detects development mode through the `DEV_MODE` environment variable:

- **Production**: `DEV_MODE=false` or not set
- **Development**: `DEV_MODE=true`

## 📊 Data Storage

- **User Data**: Stored in `data/users.json` with bcrypt password hashing
- **Student Data**: Uses existing `app/Images/Students/students.json`
- **Attendance Data**: Uses existing `app/attendance.csv`
- **Development State**: Preserved in `.dev_state.json` during development

## 📝 Notes

- Development mode preserves your current page and app state during hot reloads
- The app automatically watches for changes in the `app/` directory
- Press `Ctrl+C` to stop the development server
- All pages are modular and can be easily extended
- Authentication system uses industry-standard bcrypt for password security
- User data is automatically backed up and managed by the JSON store service
- **Shell page removed** - simplified navigation structure
- **Home page is the landing page** with login/register options
- **Main app has sidebar navigation** for Dashboard, Students, and Attendance

## 🧪 Testing

The authentication system can be tested independently:

```bash
# Test authentication functionality
python test_auth.py

# This will create test users and demonstrate:
# - User registration
# - User login/logout
# - Password validation
# - User management
```
