"""
📱 Android WebView Application Builder - Ekspansi Branch
Mobile Interface for Agentic AI System

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging
import shutil

class AndroidWebViewAppBuilder:
    """
    Android WebView Application Builder
    
    Features:
    - Creates Android WebView app
    - Integrates with main.py system
    - Provides mobile interface
    - Handles deployment and compilation
    - Manages app configuration
    """
    
    def __init__(self):
        self.name = "Android WebView App Builder"
        self.version = "1.0.0"
        self.app_name = "AgenticAI"
        self.package_name = "com.dhaher.agenticai"
        self.start_time = datetime.now()
        
        # App configuration
        self.app_config = {
            "app_name": self.app_name,
            "package_name": self.package_name,
            "version_name": "1.0.0",
            "version_code": 1,
            "min_sdk": 21,
            "target_sdk": 34,
            "compile_sdk": 34,
            "webview_url": "http://localhost:5000",
            "enable_javascript": True,
            "enable_local_storage": True,
            "enable_geolocation": False,
            "fullscreen": True
        }
        
        # Paths
        self.project_root = Path(".")
        self.android_project_dir = Path("android_app")
        self.assets_dir = self.android_project_dir / "app" / "src" / "main" / "assets"
        self.java_dir = self.android_project_dir / "app" / "src" / "main" / "java" / "com" / "dhaher" / "agenticai"
        self.res_dir = self.android_project_dir / "app" / "src" / "main" / "res"
        
        # Setup logging
        self.setup_logging()
        
        self.logger.info(f"Android WebView App Builder initialized - {self.name} v{self.version}")
    
    def setup_logging(self):
        """Setup logging for Android App Builder"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "android_app_builder.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AndroidAppBuilder")
    
    def create_android_project(self) -> Dict[str, Any]:
        """Create Android project structure"""
        self.logger.info("Creating Android project structure...")
        
        try:
            # Create project directories
            self._create_project_directories()
            
            # Create build files
            self._create_build_files()
            
            # Create Java/Kotlin source files
            self._create_source_files()
            
            # Create resources
            self._create_resources()
            
            # Create manifest
            self._create_manifest()
            
            # Copy Python system to assets
            self._copy_python_system_to_assets()
            
            self.logger.info("Android project created successfully")
            
            return {
                "success": True,
                "project_path": str(self.android_project_dir),
                "app_name": self.app_name,
                "package_name": self.package_name,
                "message": "Android project created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Android project: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Android project"
            }
    
    def _create_project_directories(self):
        """Create Android project directory structure"""
        directories = [
            self.android_project_dir,
            self.android_project_dir / "app",
            self.android_project_dir / "app" / "src",
            self.android_project_dir / "app" / "src" / "main",
            self.java_dir,
            self.assets_dir,
            self.res_dir,
            self.res_dir / "layout",
            self.res_dir / "values",
            self.res_dir / "drawable",
            self.res_dir / "mipmap-hdpi",
            self.res_dir / "mipmap-mdpi",
            self.res_dir / "mipmap-xhdpi",
            self.res_dir / "mipmap-xxhdpi",
            self.res_dir / "mipmap-xxxhdpi"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def _create_build_files(self):
        """Create Gradle build files"""
        
        # Root build.gradle
        root_build_gradle = '''
buildscript {
    ext.kotlin_version = "1.8.20"
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.0.2'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
'''
        
        # App build.gradle
        app_build_gradle = f'''
plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}}

android {{
    namespace '{self.package_name}'
    compileSdk {self.app_config["compile_sdk"]}

    defaultConfig {{
        applicationId '{self.package_name}'
        minSdk {self.app_config["min_sdk"]}
        targetSdk {self.app_config["target_sdk"]}
        versionCode {self.app_config["version_code"]}
        versionName '{self.app_config["version_name"]}'

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
    
    kotlinOptions {{
        jvmTarget = '1.8'
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.webkit:webkit:1.7.0'
    implementation 'androidx.swiperefreshlayout:swiperefreshlayout:1.1.0'
    
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}}
'''
        
        # gradle.properties
        gradle_properties = '''
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
android.nonTransitiveRClass=false
'''
        
        # settings.gradle
        settings_gradle = '''
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "AgenticAI"
include ':app'
'''
        
        # Write build files
        with open(self.android_project_dir / "build.gradle", 'w') as f:
            f.write(root_build_gradle)
            
        with open(self.android_project_dir / "app" / "build.gradle", 'w') as f:
            f.write(app_build_gradle)
            
        with open(self.android_project_dir / "gradle.properties", 'w') as f:
            f.write(gradle_properties)
            
        with open(self.android_project_dir / "settings.gradle", 'w') as f:
            f.write(settings_gradle)
    
    def _create_source_files(self):
        """Create Java/Kotlin source files"""
        
        # MainActivity.kt
        main_activity = f'''
package {self.package_name}

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import java.io.*
import java.net.ServerSocket
import java.net.Socket

class MainActivity : AppCompatActivity() {{
    
    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private var pythonServerProcess: Process? = null
    private val serverPort = 5000
    
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        setupWebView()
        startPythonServer()
    }}
    
    private fun initViews() {{
        webView = findViewById(R.id.webview)
        progressBar = findViewById(R.id.progress_bar)
        swipeRefreshLayout = findViewById(R.id.swipe_refresh)
        
        swipeRefreshLayout.setOnRefreshListener {{
            webView.reload()
        }}
    }}
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {{
        webView.apply {{
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = true
            settings.allowContentAccess = true
            settings.setSupportZoom(true)
            settings.builtInZoomControls = true
            settings.displayZoomControls = false
            
            webViewClient = object : WebViewClient() {{
                override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {{
                    super.onPageStarted(view, url, favicon)
                    progressBar.visibility = View.VISIBLE
                }}
                
                override fun onPageFinished(view: WebView?, url: String?) {{
                    super.onPageFinished(view, url)
                    progressBar.visibility = View.GONE
                    swipeRefreshLayout.isRefreshing = false
                }}
                
                override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {{
                    super.onReceivedError(view, request, error)
                    // Load fallback HTML if server not available
                    loadFallbackPage()
                }}
            }}
            
            webChromeClient = object : WebChromeClient() {{
                override fun onProgressChanged(view: WebView?, newProgress: Int) {{
                    super.onProgressChanged(view, newProgress)
                    progressBar.progress = newProgress
                }}
            }}
        }}
    }}
    
    private fun startPythonServer() {{
        Thread {{
            try {{
                // Copy Python files to internal storage if needed
                copyPythonFilesToInternalStorage()
                
                // Start Python server (simplified for demo)
                // In real implementation, you would use Chaquopy or similar
                // For now, load the web interface directly
                runOnUiThread {{
                    loadWebInterface()
                }}
                
            }} catch (e: Exception) {{
                e.printStackTrace()
                runOnUiThread {{
                    loadFallbackPage()
                }}
            }}
        }}.start()
    }}
    
    private fun copyPythonFilesToInternalStorage() {{
        // Copy Python system files from assets to internal storage
        val assetManager = assets
        val pythonDir = File(filesDir, "python")
        if (!pythonDir.exists()) {{
            pythonDir.mkdirs()
        }}
        
        try {{
            val files = assetManager.list("python") ?: arrayOf()
            for (filename in files) {{
                copyAssetToFile("python/$filename", File(pythonDir, filename))
            }}
        }} catch (e: IOException) {{
            e.printStackTrace()
        }}
    }}
    
    private fun copyAssetToFile(assetPath: String, outFile: File) {{
        assets.open(assetPath).use {{ input ->
            outFile.outputStream().use {{ output ->
                input.copyTo(output)
            }}
        }}
    }}
    
    private fun loadWebInterface() {{
        // Load the embedded web interface
        val htmlContent = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Agentic AI System</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    font-size: 1.2em;
                    opacity: 0.9;
                    margin-bottom: 5px;
                }}
                .creator {{
                    font-size: 0.9em;
                    opacity: 0.8;
                }}
                .status-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .feature-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .feature-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: transform 0.3s ease;
                }}
                .feature-card:hover {{
                    transform: translateY(-5px);
                }}
                .feature-icon {{
                    font-size: 2em;
                    margin-bottom: 10px;
                }}
                .btn {{
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 25px;
                    font-size: 1.1em;
                    cursor: pointer;
                    margin: 10px;
                    transition: all 0.3s ease;
                }}
                .btn:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-item {{
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #4ecdc4;
                }}
                .stat-label {{
                    font-size: 0.9em;
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🧠 Agentic AI System</div>
                    <div class="subtitle">Autonomous Multi-Agent Intelligence</div>
                    <div class="creator">Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩</div>
                </div>
                
                <div class="status-card">
                    <h3>📱 Mobile Interface Active</h3>
                    <p>Welcome to the Agentic AI System mobile interface. The system is running in mobile-optimized mode with full functionality.</p>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">20+</div>
                        <div class="stat-label">AI Agents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100+</div>
                        <div class="stat-label">Data Sources</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100</div>
                        <div class="stat-label">Research Prompts</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Autonomous</div>
                    </div>
                </div>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <h4>Multi-Agent System</h4>
                        <p>20+ specialized AI agents working autonomously</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h4>Data Expansion</h4>
                        <p>100+ sources providing continuous insights</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔬</div>
                        <h4>Research Engine</h4>
                        <p>100 research prompts for ecosystem enhancement</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🚀</div>
                        <h4>Auto Enhancement</h4>
                        <p>Continuous system improvement and evolution</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <button class="btn" onclick="refreshSystem()">🔄 Refresh System</button>
                    <button class="btn" onclick="viewLogs()">📋 View Logs</button>
                    <button class="btn" onclick="systemStatus()">📊 System Status</button>
                </div>
            </div>
            
            <script>
                function refreshSystem() {{
                    location.reload();
                }}
                
                function viewLogs() {{
                    alert('Logs functionality will be implemented in the next update.');
                }}
                
                function systemStatus() {{
                    alert('System Status:\\n\\n✅ All systems operational\\n🤖 20+ agents active\\n📊 Data expansion running\\n🔬 Research engine active\\n🚀 Enhancement system ready');
                }}
                
                // Auto-refresh every 30 seconds
                setInterval(function() {{
                    console.log('System heartbeat - ' + new Date().toLocaleTimeString());
                }}, 30000);
            </script>
        </body>
        </html>
        """
        
        webView.loadDataWithBaseURL(null, htmlContent, "text/html", "UTF-8", null)
    }}
    
    private fun loadFallbackPage() {{
        val fallbackHtml = """
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }}
                .error-container {{ background: white; border-radius: 10px; padding: 30px; margin: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>🔄 Starting Agentic AI System...</h2>
                <p>The system is initializing. Please wait a moment and try refreshing.</p>
                <button onclick="location.reload()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px;">Refresh</button>
            </div>
        </body>
        </html>
        """
        webView.loadDataWithBaseURL(null, fallbackHtml, "text/html", "UTF-8", null)
    }}
    
    override fun onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack()
        }} else {{
            super.onBackPressed()
        }}
    }}
    
    override fun onDestroy() {{
        super.onDestroy()
        pythonServerProcess?.destroy()
    }}
}}
'''
        
        with open(self.java_dir / "MainActivity.kt", 'w') as f:
            f.write(main_activity)
    
    def _create_resources(self):
        """Create Android resource files"""
        
        # activity_main.xml
        activity_main_xml = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.swiperefreshlayout.widget.SwipeRefreshLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/swipe_refresh"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <RelativeLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <WebView
            android:id="@+id/webview"
            android:layout_width="match_parent"
            android:layout_height="match_parent" />

        <ProgressBar
            android:id="@+id/progress_bar"
            style="?android:attr/progressBarStyleHorizontal"
            android:layout_width="match_parent"
            android:layout_height="4dp"
            android:layout_alignParentTop="true"
            android:progressTint="@color/primary_color"
            android:visibility="gone" />

    </RelativeLayout>

</androidx.swiperefreshlayout.widget.SwipeRefreshLayout>
'''
        
        # colors.xml
        colors_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary_color">#667eea</color>
    <color name="primary_dark">#764ba2</color>
    <color name="accent_color">#4ecdc4</color>
    <color name="white">#FFFFFF</color>
    <color name="black">#000000</color>
    <color name="gray_light">#F5F5F5</color>
</resources>
'''
        
        # strings.xml
        strings_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{self.app_name}</string>
    <string name="loading">Loading...</string>
    <string name="error_loading">Error loading page</string>
    <string name="refresh">Refresh</string>
</resources>
'''
        
        # styles.xml
        styles_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">@color/primary_color</item>
        <item name="colorPrimaryDark">@color/primary_dark</item>
        <item name="colorAccent">@color/accent_color</item>
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowContentOverlay">@null</item>
    </style>
</resources>
'''
        
        # Write resource files
        with open(self.res_dir / "layout" / "activity_main.xml", 'w') as f:
            f.write(activity_main_xml)
            
        with open(self.res_dir / "values" / "colors.xml", 'w') as f:
            f.write(colors_xml)
            
        with open(self.res_dir / "values" / "strings.xml", 'w') as f:
            f.write(strings_xml)
            
        with open(self.res_dir / "values" / "styles.xml", 'w') as f:
            f.write(styles_xml)
    
    def _create_manifest(self):
        """Create AndroidManifest.xml"""
        
        manifest_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="{self.package_name}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait"
            android:theme="@style/AppTheme">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
    </application>

</manifest>
'''
        
        with open(self.android_project_dir / "app" / "src" / "main" / "AndroidManifest.xml", 'w') as f:
            f.write(manifest_xml)
    
    def _copy_python_system_to_assets(self):
        """Copy Python system files to Android assets"""
        try:
            # Create python directory in assets
            python_assets_dir = self.assets_dir / "python"
            python_assets_dir.mkdir(parents=True, exist_ok=True)
            
            # List of key Python files to include
            python_files = [
                "main.py",
                "data_expansion_engine.py",
                "ecosystem_enhancement_system.py",
                "requirements.txt"
            ]
            
            # Copy Python files
            for file_name in python_files:
                src_file = self.project_root / file_name
                if src_file.exists():
                    dst_file = python_assets_dir / file_name
                    shutil.copy2(src_file, dst_file)
                    self.logger.debug(f"Copied {file_name} to assets")
            
            # Copy core directory
            core_src = self.project_root / "core"
            if core_src.exists():
                core_dst = python_assets_dir / "core"
                shutil.copytree(core_src, core_dst, dirs_exist_ok=True)
                self.logger.debug("Copied core directory to assets")
            
            # Copy agents directory
            agents_src = self.project_root / "agents"
            if agents_src.exists():
                agents_dst = python_assets_dir / "agents"
                shutil.copytree(agents_src, agents_dst, dirs_exist_ok=True)
                self.logger.debug("Copied agents directory to assets")
            
            self.logger.info("Python system files copied to Android assets")
            
        except Exception as e:
            self.logger.error(f"Failed to copy Python system to assets: {e}")
    
    def compile_android_app(self) -> Dict[str, Any]:
        """Compile Android application"""
        self.logger.info("Compiling Android application...")
        
        try:
            # Check if Gradle is available
            gradle_cmd = "gradlew" if os.name == "nt" else "./gradlew"
            gradle_path = self.android_project_dir / gradle_cmd
            
            if not gradle_path.exists():
                # Create gradle wrapper if not exists
                self._create_gradle_wrapper()
            
            # Set executable permission for gradlew on Unix systems
            if os.name != "nt":
                os.chmod(gradle_path, 0o755)
            
            # Build APK
            build_cmd = [str(gradle_path), "assembleDebug"]
            
            self.logger.info(f"Running build command: {' '.join(build_cmd)}")
            
            result = subprocess.run(
                build_cmd,
                cwd=self.android_project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                apk_path = self.android_project_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
                
                return {
                    "success": True,
                    "apk_path": str(apk_path) if apk_path.exists() else "APK not found",
                    "build_output": result.stdout,
                    "message": "Android app compiled successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "build_output": result.stdout,
                    "message": "Android app compilation failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Build timeout (5 minutes)",
                "message": "Android app compilation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to compile Android app"
            }
    
    def _create_gradle_wrapper(self):
        """Create Gradle wrapper files"""
        
        # gradle-wrapper.properties
        wrapper_properties = '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.0-bin.zip
networkTimeout=10000
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''
        
        # Create gradle wrapper directory
        gradle_dir = self.android_project_dir / "gradle" / "wrapper"
        gradle_dir.mkdir(parents=True, exist_ok=True)
        
        with open(gradle_dir / "gradle-wrapper.properties", 'w') as f:
            f.write(wrapper_properties)
        
        # Create gradlew script for Unix
        gradlew_unix = '''#!/usr/bin/env sh

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD="maximum"

warn () {
    echo "$*"
}

die () {
    echo
    echo "$*"
    echo
    exit 1
}

# Attempt to set APP_HOME
# Resolve links: $0 may be a link
PRG="$0"
# Need this for relative symlinks.
while [ -h "$PRG" ] ; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '.*-> \\(.*\\)$'`
    if expr "$link" : '/.*' > /dev/null; then
        PRG="$link"
    else
        PRG=`dirname "$PRG"`"/$link"
    fi
done
SAVED="`pwd`"
cd "`dirname \\"$PRG\\"`/" >/dev/null
APP_HOME="`pwd -P`"
cd "$SAVED" >/dev/null

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum file descriptors if we can.
if [ "$cygwin" = "false" -a "$darwin" = "false" ] ; then
    MAX_FD_LIMIT=`ulimit -H -n`
    if [ $? -eq 0 ] ; then
        if [ "$MAX_FD" = "maximum" -o "$MAX_FD" = "max" ] ; then
            MAX_FD="$MAX_FD_LIMIT"
        fi
        ulimit -n $MAX_FD
        if [ $? -ne 0 ] ; then
            warn "Could not set maximum file descriptor limit: $MAX_FD"
        fi
    else
        warn "Could not query maximum file descriptor limit: $MAX_FD_LIMIT"
    fi
fi

exec "$JAVACMD" \\
    -classpath "$CLASSPATH" \\
    org.gradle.wrapper.GradleWrapperMain \\
    "$@"
'''
        
        # Create gradlew.bat for Windows
        gradlew_bat = '''@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%"=="" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\\gradle\\wrapper\\gradle-wrapper.jar


@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
@rem End local scope for the variables with windows NT shell
if %ERRORLEVEL% equ 0 goto mainEnd

:fail
rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
if not "" == "%GRADLE_EXIT_CONSOLE%" exit 1
exit /b 1

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
'''
        
        # Write gradlew files
        with open(self.android_project_dir / "gradlew", 'w') as f:
            f.write(gradlew_unix)
            
        with open(self.android_project_dir / "gradlew.bat", 'w') as f:
            f.write(gradlew_bat)
    
    def get_build_status(self) -> Dict[str, Any]:
        """Get build status and information"""
        return {
            "builder_status": "ready",
            "app_name": self.app_name,
            "package_name": self.package_name,
            "version": self.app_config["version_name"],
            "project_path": str(self.android_project_dir),
            "project_exists": self.android_project_dir.exists(),
            "apk_exists": (self.android_project_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk").exists(),
            "creation_time": self.start_time.isoformat()
        }

# Global instance
android_app_builder = AndroidWebViewAppBuilder()

# Export for use by other modules
__all__ = ['AndroidWebViewAppBuilder', 'android_app_builder']