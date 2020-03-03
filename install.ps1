python -m venv ./venv-windows
./venv-windows/Scripts/activate
python -m pip install -r requirements.txt

$Shell = New-Object -ComObject ("WScript.Shell")
$ShortCut = $Shell.CreateShortcut((pwd).Path + "\run_server.lnk")
$ShortCut.TargetPath= (pwd).Path + "\venv-windows\Scripts\pythonw.exe"
$ShortCut.Arguments="-m chat.server.qt_server"
$ShortCut.WorkingDirectory = (pwd).Path;
$ShortCut.WindowStyle = 1;
$ShortCut.Description = "Qt chat server";
$ShortCut.Save()

$ShortCut = $Shell.CreateShortcut((pwd).Path + "\run_client.lnk")
$ShortCut.TargetPath= (pwd).Path + "\venv-windows\Scripts\pythonw.exe"
$ShortCut.Arguments="-m chat.client.client_setup"
$ShortCut.WorkingDirectory = (pwd).Path;
$ShortCut.WindowStyle = 1;
$ShortCut.Description = "Qt chat client";
$ShortCut.Save()