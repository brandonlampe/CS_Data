Attribute VB_Name = "modRmRows"
Public mnu As CommandBarButton

Sub ClearExcessRowsAndColumns()
    Dim ar As Range, r As Long, c As Long, tr As Long, tc As Long, x As Range
    Dim wksWks As Worksheet, ur As Range, arCount As Integer, i As Integer
    Dim blProtCont As Boolean, blProtScen As Boolean, blProtDO As Boolean
    Dim shp As Shape

    If ActiveWorkbook Is Nothing Then Exit Sub

    On Error Resume Next
    For Each wksWks In ActiveWorkbook.Worksheets
        Err.Clear
        Set ur = Nothing
        'Store worksheet protection settings and unprotect if protected.
        blProtCont = wksWks.ProtectContents
        blProtDO = wksWks.ProtectDrawingObjects
        blProtScen = wksWks.ProtectScenarios
        wksWks.Unprotect ""
        If Err.Number = 1004 Then
            Err.Clear
            MsgBox "'" & wksWks.Name & _
                   "' is protected with a password and cannot be checked." _
                 , vbInformation
        Else
            Application.StatusBar = "Checking " & wksWks.Name & _
                                    ", Please Wait..."
            r = 0
            c = 0

            'Determine if the sheet contains both formulas and constants
            Set ur = Union(wksWks.UsedRange.SpecialCells(xlCellTypeConstants), _
                           wksWks.UsedRange.SpecialCells(xlCellTypeFormulas))
            'If both fails, try constants only
            If Err.Number = 1004 Then
                Err.Clear
                Set ur = wksWks.UsedRange.SpecialCells(xlCellTypeConstants)
            End If
            'If constants fails then set it to formulas
            If Err.Number = 1004 Then
                Err.Clear
                Set ur = wksWks.UsedRange.SpecialCells(xlCellTypeFormulas)
            End If
            'If there is still an error then the worksheet is empty
            If Err.Number <> 0 Then
                Err.Clear
                If wksWks.UsedRange.Address <> "$A$1" Then
                    wksWks.UsedRange.EntireRow.Hidden = False
                    wksWks.UsedRange.EntireColumn.Hidden = False
                    wksWks.UsedRange.EntireRow.RowHeight = _
                    IIf(wksWks.StandardHeight <> 12.75, 12.75, 13)
                    wksWks.UsedRange.EntireColumn.ColumnWidth = 10
                    wksWks.UsedRange.EntireRow.Clear
                    'Reset column width which can also _
                     cause the lastcell to be innacurate
                    wksWks.UsedRange.EntireColumn.ColumnWidth = _
                    wksWks.StandardWidth
                    'Reset row height which can also cause the _
                     lastcell to be innacurate
                    If wksWks.StandardHeight < 1 Then
                        wksWks.UsedRange.EntireRow.RowHeight = 12.75
                    Else
                        wksWks.UsedRange.EntireRow.RowHeight = _
                        wksWks.StandardHeight
                    End If
                Else
                    Set ur = Nothing
                End If
            End If
            'On Error GoTo 0
            If Not ur Is Nothing Then
                arCount = ur.Areas.Count
                'determine the last column and row that contains data or formula
                For Each ar In ur.Areas
                    i = i + 1
                    tr = ar.Range("A1").Row + ar.Rows.Count - 1
                    tc = ar.Range("A1").Column + ar.Columns.Count - 1
                    If tc > c Then c = tc
                    If tr > r Then r = tr
                Next
                'Determine the area covered by shapes
                'so we don't remove shading behind shapes
                For Each shp In wksWks.Shapes
                    tr = shp.BottomRightCell.Row
                    tc = shp.BottomRightCell.Column
                    If tc > c Then c = tc
                    If tr > r Then r = tr
                Next
                Application.StatusBar = "Clearing Excess Cells in " & _
                                        wksWks.Name & ", Please Wait..."
                If r < wksWks.Rows.Count And r < wksWks.Cells.SpecialCells(xlCellTypeLastCell).Row Then
                    Set ur = wksWks.Rows(r + 1 & ":" & wksWks.Cells.SpecialCells(xlCellTypeLastCell).Row)
                    ur.EntireRow.Hidden = False
                    ur.EntireRow.RowHeight = IIf(wksWks.StandardHeight <> 12.75, _
                                                 12.75, 13)
                    'Reset row height which can also cause the _
                     lastcell to be innacurate
                    If wksWks.StandardHeight < 1 Then
                        ur.RowHeight = 12.75
                    Else
                        ur.RowHeight = wksWks.StandardHeight
                    End If
                    Set x = ur.Dependents
                    If Err.Number = 0 Then
                        ur.Clear
                    Else
                        Err.Clear
                        ur.Delete
                    End If
                End If
                If c < wksWks.Columns.Count And c < wksWks.Cells.SpecialCells(xlCellTypeLastCell).Column Then
                    Set ur = wksWks.Range(wksWks.Cells(1, c + 1), _
                                          wksWks.Cells(1, wksWks.Cells.SpecialCells(xlCellTypeLastCell).Column)).EntireColumn
                    ur.EntireColumn.Hidden = False
                    ur.ColumnWidth = 18

                    'Reset column width which can _
                     also cause the lastcell to be innacurate
                    ur.EntireColumn.ColumnWidth = _
                    wksWks.StandardWidth

                    Set x = ur.Dependents
                    If Err.Number = 0 Then
                        ur.Clear
                    Else
                        Err.Clear
                        ur.Delete
                    End If
                End If
            End If
        End If
        'Reset protection.
        wksWks.Protect "", blProtDO, blProtCont, blProtScen
        Err.Clear
    Next
    Application.StatusBar = False
    MsgBox "'" & ActiveWorkbook.Name & _
           "' has been cleared of excess formatting." & Chr(13) & _
           "You must save the file to keep the changes.", vbInformation
End Sub

