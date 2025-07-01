#!/usr/bin/env bash

# Agentic AI Indonesia - Android APK Build Script
# Version: 6.0.0-indonesia
# Creates ready-to-use Android APK
# Created by: Mulky Malikul Dhaher

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🇮🇩 Building Agentic AI Indonesia Android APK${NC}"
echo -e "${CYAN}Mobile-First AI Revolution v6.0.0${NC}"
echo

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${RED}❌ ANDROID_HOME not set. Please install Android SDK.${NC}"
    exit 1
fi

# Create Android project structure
echo -e "${BLUE}📁 Creating Android project structure...${NC}"
mkdir -p android-app/{app/src/main/{java/com/agentic/ai/indonesia,res/{layout,values,drawable,mipmap-hdpi,mipmap-mdpi,mipmap-xhdpi,mipmap-xxhdpi,mipmap-xxxhdpi}},gradle/wrapper}

# Create build.gradle (Project)
cat > android-app/build.gradle << 'EOF'
buildscript {
    ext.kotlin_version = '1.9.10'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.2'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }
    }
}
EOF

# Create app/build.gradle
cat > android-app/app/build.gradle << 'EOF'
apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'

android {
    compileSdkVersion 34
    buildToolsVersion "34.0.0"
    
    defaultConfig {
        applicationId "com.agentic.ai.indonesia"
        minSdkVersion 24
        targetSdkVersion 34
        versionCode 600001
        versionName "6.0.0-indonesia"
        
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.debug
        }
        debug {
            debuggable true
            minifyEnabled false
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = '1.8'
    }
    
    packagingOptions {
        pickFirst '**/libc++_shared.so'
        pickFirst '**/libjsc.so'
        exclude 'META-INF/DEPENDENCIES'
        exclude 'META-INF/LICENSE'
        exclude 'META-INF/LICENSE.txt'
        exclude 'META-INF/NOTICE'
        exclude 'META-INF/NOTICE.txt'
    }
}

dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib:$kotlin_version"
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.1'
    
    // Speech Recognition & TTS
    implementation 'androidx.speech:speech:1.0.0'
    
    // HTTP Client
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // Local Database
    implementation 'androidx.room:room-runtime:2.6.0'
    implementation 'androidx.room:room-ktx:2.6.0'
    
    // Security
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'
    
    // WebView
    implementation 'androidx.webkit:webkit:1.8.0'
    
    // Permissions
    implementation 'androidx.activity:activity-ktx:1.8.1'
    
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
EOF

# Create AndroidManifest.xml
cat > android-app/app/src/main/AndroidManifest.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.agentic.ai.indonesia">
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.MICROPHONE" />
    
    <application
        android:name=".AgenticAIApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait"
            android:theme="@style/AppTheme.NoActionBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <activity
            android:name=".VoiceActivity"
            android:exported="false"
            android:screenOrientation="portrait"
            android:theme="@style/AppTheme.NoActionBar" />
            
        <activity
            android:name=".AgentActivity"
            android:exported="false"
            android:screenOrientation="portrait"
            android:theme="@style/AppTheme.NoActionBar" />
            
        <service
            android:name=".AIService"
            android:enabled="true"
            android:exported="false" />
            
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
EOF

# Create MainActivity.kt
cat > android-app/app/src/main/java/com/agentic/ai/indonesia/MainActivity.kt << 'EOF'
package com.agentic.ai.indonesia

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {
    
    private lateinit var tvWelcome: TextView
    private lateinit var btnVoiceCommand: Button
    private lateinit var btnAgents: Button
    private lateinit var btnSettings: Button
    
    private val RECORD_AUDIO_PERMISSION_CODE = 1001
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        checkPermissions()
        setupClickListeners()
    }
    
    private fun initViews() {
        tvWelcome = findViewById(R.id.tv_welcome)
        btnVoiceCommand = findViewById(R.id.btn_voice_command)
        btnAgents = findViewById(R.id.btn_agents)
        btnSettings = findViewById(R.id.btn_settings)
        
        tvWelcome.text = "🇮🇩 Selamat datang di Agentic AI Indonesia v6.0.0\n" +
                "Platform AI Agentic Pertama di Indonesia"
    }
    
    private fun checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                arrayOf(Manifest.permission.RECORD_AUDIO), 
                RECORD_AUDIO_PERMISSION_CODE)
        }
    }
    
    private fun setupClickListeners() {
        btnVoiceCommand.setOnClickListener {
            startVoiceActivity()
        }
        
        btnAgents.setOnClickListener {
            startAgentActivity()
        }
        
        btnSettings.setOnClickListener {
            Toast.makeText(this, "🔧 Pengaturan akan segera tersedia!", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun startVoiceActivity() {
        val intent = Intent(this, VoiceActivity::class.java)
        startActivity(intent)
    }
    
    private fun startAgentActivity() {
        val intent = Intent(this, AgentActivity::class.java)
        startActivity(intent)
    }
    
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            RECORD_AUDIO_PERMISSION_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "🎤 Izin microphone diberikan!", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "❌ Izin microphone diperlukan untuk voice commands", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
EOF

# Create layout files
cat > android-app/app/src/main/res/layout/activity_main.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:background="@color/background_color">

    <ImageView
        android:layout_width="120dp"
        android:layout_height="120dp"
        android:layout_gravity="center_horizontal"
        android:layout_marginTop="40dp"
        android:src="@drawable/ic_agentic_logo"
        android:contentDescription="Agentic AI Indonesia Logo" />

    <TextView
        android:id="@+id/tv_welcome"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="32dp"
        android:text="🇮🇩 Agentic AI Indonesia"
        android:textSize="24sp"
        android:textStyle="bold"
        android:textColor="@color/primary_text"
        android:gravity="center"
        android:lineSpacingExtra="4dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Platform AI Agentic Pertama di Indonesia\nMobile-First AI Revolution"
        android:textSize="16sp"
        android:textColor="@color/secondary_text"
        android:gravity="center"
        android:lineSpacingExtra="2dp" />

    <Button
        android:id="@+id/btn_voice_command"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:layout_marginTop="48dp"
        android:background="@drawable/button_primary"
        android:text="🗣️ Voice Commands"
        android:textColor="@android:color/white"
        android:textSize="18sp"
        android:textStyle="bold"
        android:elevation="4dp" />

    <Button
        android:id="@+id/btn_agents"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:layout_marginTop="16dp"
        android:background="@drawable/button_secondary"
        android:text="🤖 AI Agents"
        android:textColor="@color/primary_color"
        android:textSize="18sp"
        android:textStyle="bold"
        android:elevation="2dp" />

    <Button
        android:id="@+id/btn_settings"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:layout_marginTop="16dp"
        android:background="@drawable/button_secondary"
        android:text="⚙️ Pengaturan"
        android:textColor="@color/primary_color"
        android:textSize="18sp"
        android:elevation="2dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="32dp"
        android:text="💡 Katakan \"Halo Agen AI\" untuk memulai voice commands"
        android:textSize="14sp"
        android:textColor="@color/hint_text"
        android:gravity="center"
        android:background="@drawable/hint_background"
        android:padding="16dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:text="🇮🇩 Dibuat dengan ❤️ di Indonesia oleh Mulky Malikul Dhaher"
        android:textSize="12sp"
        android:textColor="@color/secondary_text"
        android:gravity="center" />

</LinearLayout>
EOF

# Create strings.xml
cat > android-app/app/src/main/res/values/strings.xml << 'EOF'
<resources>
    <string name="app_name">Agentic AI Indonesia</string>
    <string name="voice_command_title">Voice Commands</string>
    <string name="agents_title">AI Agents</string>
    <string name="settings_title">Pengaturan</string>
    <string name="listening">Mendengarkan...</string>
    <string name="processing">Memproses...</string>
    <string name="voice_activation">Katakan "Halo Agen AI" untuk memulai</string>
</resources>
EOF

# Create colors.xml
cat > android-app/app/src/main/res/values/colors.xml << 'EOF'
<resources>
    <color name="primary_color">#FF0000</color>
    <color name="primary_dark">#CC0000</color>
    <color name="accent_color">#2196F3</color>
    <color name="background_color">#F5F5F5</color>
    <color name="surface_color">#FFFFFF</color>
    <color name="primary_text">#212121</color>
    <color name="secondary_text">#757575</color>
    <color name="hint_text">#9E9E9E</color>
    <color name="divider_color">#BDBDBD</color>
</resources>
EOF

# Create styles.xml
cat > android-app/app/src/main/res/values/styles.xml << 'EOF'
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <item name="colorPrimary">@color/primary_color</item>
        <item name="colorPrimaryDark">@color/primary_dark</item>
        <item name="colorAccent">@color/accent_color</item>
        <item name="android:windowBackground">@color/background_color</item>
    </style>
    
    <style name="AppTheme.NoActionBar">
        <item name="windowActionBar">false</item>
        <item name="windowNoTitle">true</item>
    </style>
</resources>
EOF

# Create drawables
mkdir -p android-app/app/src/main/res/drawable

cat > android-app/app/src/main/res/drawable/button_primary.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <gradient
        android:startColor="#FF0000"
        android:endColor="#CC0000"
        android:angle="90" />
    <corners android:radius="12dp" />
</shape>
EOF

cat > android-app/app/src/main/res/drawable/button_secondary.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="@android:color/white" />
    <stroke android:width="2dp" android:color="@color/primary_color" />
    <corners android:radius="12dp" />
</shape>
EOF

# Create Gradle Wrapper properties
cat > android-app/gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-all.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

# Create settings.gradle
cat > android-app/settings.gradle << 'EOF'
include ':app'
rootProject.name = "Agentic AI Indonesia"
EOF

# Build the APK
echo -e "${BLUE}🔨 Building Android APK...${NC}"
cd android-app

# Clean and build
echo -e "${BLUE}🧹 Cleaning project...${NC}"
./gradlew clean

echo -e "${BLUE}📦 Building release APK...${NC}"
./gradlew assembleRelease

# Check if APK was built successfully
if [ -f "app/build/outputs/apk/release/app-release.apk" ]; then
    echo -e "${GREEN}✅ APK built successfully!${NC}"
    
    # Rename APK
    mv app/build/outputs/apk/release/app-release.apk ../agentic-ai-indonesia-v6.0.0.apk
    
    echo -e "${GREEN}📱 APK location: agentic-ai-indonesia-v6.0.0.apk${NC}"
    echo -e "${GREEN}📁 Size: $(du -h ../agentic-ai-indonesia-v6.0.0.apk | cut -f1)${NC}"
    
    # Create checksums
    echo -e "${BLUE}🔐 Creating checksums...${NC}"
    cd ..
    sha256sum agentic-ai-indonesia-v6.0.0.apk > agentic-ai-indonesia-v6.0.0.apk.sha256
    md5sum agentic-ai-indonesia-v6.0.0.apk > agentic-ai-indonesia-v6.0.0.apk.md5
    
    echo
    echo -e "${GREEN}🎉 Android APK build completed successfully!${NC}"
    echo
    echo -e "${YELLOW}📱 Installation Instructions:${NC}"
    echo -e "   1. Transfer APK to your Android device"
    echo -e "   2. Enable 'Unknown Sources' in Settings"
    echo -e "   3. Install the APK"
    echo -e "   4. Launch 'Agentic AI Indonesia'"
    echo
    echo -e "${CYAN}🗣️ First Voice Command: \"Halo Agen AI\"${NC}"
    
else
    echo -e "${RED}❌ APK build failed!${NC}"
    echo -e "${YELLOW}Check the build logs above for errors.${NC}"
    exit 1
fi