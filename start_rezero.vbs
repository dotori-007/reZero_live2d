Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

strPython = "C:\2026591001\Python_3.10.11_64\pythonw.exe"
If Not fso.FileExists(strPython) Then
    strPython = "pythonw.exe"
End If

WshShell.CurrentDirectory = strPath
WshShell.Run Chr(34) & strPython & Chr(34) & " " & Chr(34) & strPath & "\app.py" & Chr(34), 0, False
Set WshShell = Nothing
Set fso = Nothing
