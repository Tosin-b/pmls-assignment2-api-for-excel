    Attribute VB_Name = "RefreshCampaignAnalysis"
Sub RefreshCampaignAnalysis()
    ' pull the latest tables from the API
    ActiveWorkbook.RefreshAll
    MsgBox "Campaign analysis refreshed."
End Sub
