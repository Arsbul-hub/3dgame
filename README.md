Для создания exe файла используйте комманду:
pyinstaller --noconfirm --onefile --windowed --add-data "C:/users/arsbul/Рабочий стол/3dgame/app;app/" --add-data "C:/users/arsbul/Рабочий стол/3dgame/panda_config.prc;." --add-data "C:/users/arsbul/Рабочий стол/3dgame/config.json;." --add-data "C:/users/arsbul/Рабочий стол/3dgame/arial.ttf;." --add-data "C:/users/arsbul/AppData/Local;Local/" --add-data "C:/users/arsbul/Local Settings/Application Data/Programs/Python/Python310/Lib/site-packages/panda3d;panda3d/"  "C:/users/arsbul/Рабочий стол/3dgame/main.py"
