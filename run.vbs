Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
WshShell.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)

' 1) 优先 WorkBuddy 自带 Python（支持通配符版本号）
Dim userProfile, wbPyDir, folder, pywPath, pythonPath
userProfile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
wbPyDir = userProfile & "\.workbuddy\binaries\python\versions\"

pywPath = ""
pythonPath = ""
If fso.FolderExists(wbPyDir) Then
    For Each folder In fso.GetFolder(wbPyDir).SubFolders
        If Left(folder.Name, 2) = "3." Then
            If pywPath = "" Then
                pywPath = folder.Path & "\pythonw.exe"
            End If
            If pythonPath = "" Then
                pythonPath = folder.Path & "\python.exe"
            End If
        End If
    Next
End If

' 2) 尝试运行
If pywPath <> "" And fso.FileExists(pywPath) Then
    WshShell.Run """" & pywPath & """ app.py", 0, False
ElseIf pythonPath <> "" And fso.FileExists(pythonPath) Then
    WshShell.Run """" & pythonPath & """ app.py", 0, False
Else
    ' 回退到 PATH
    On Error Resume Next
    WshShell.Run "pythonw app.py", 0, False
    If Err.Number <> 0 Then
        Err.Clear
        WshShell.Run "python app.py", 0, False
    End If
    On Error Goto 0
End If
