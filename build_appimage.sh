#!/bin/bash
set -e
echo "🔨 Сборка TaskMaster AppImage"
echo "================================"

# Очистка
rm -rf build dist

# Проверяем иконку
if [ ! -f "icon.png" ]; then
    echo "❌ Иконка не найдена! Копирую из домашней директории..."
    cp ~/red_windows_red_folder_folder_icon_250635.png icon.png
fi

echo "✅ Иконка готова"

# Сборка с PyInstaller
echo "📦 Сборка исполняемого файла..."
pyinstaller \
    --name="TaskMaster" \
    --windowed \
    --onefile \
    --add-data="icon.png:." \
    --icon=icon.png \
    main.py

echo "✅ Исполняемый файл создан"

# AppDir
APPDIR="build/TaskMaster.AppDir"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/applications"

cp "dist/TaskMaster" "$APPDIR/usr/bin/"
cp "icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/TaskMaster.png"
cp "icon.png" "$APPDIR/TaskMaster.png"

cat > "$APPDIR/usr/share/applications/TaskMaster.desktop" << EOF
[Desktop Entry]
Name=TaskMaster
Comment=Менеджер задач
Exec=TaskMaster
Icon=TaskMaster
Type=Application
Categories=Utility;Office;
Terminal=false
EOF

cp "$APPDIR/usr/share/applications/TaskMaster.desktop" "$APPDIR/"

cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/TaskMaster" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# appimagetool
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Загрузка appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Сборка
echo "🎁 Сборка AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "$APPDIR" "dist/TaskMaster-Linux-x86_64.AppImage"

echo ""
echo "✅ ГОТОВО!"
echo "Запуск: ./dist/TaskMaster-Linux-x86_64.AppImage"
