// Fill out your copyright notice in the Description page of Project Settings.
//
//Python to list functions in this class: 
//for i in sorted(dir(unreal.ZspcCpp)):
//print(i)


#include "ZspcCpp.h"
#include "IContentBrowserSingleton.h"
#include "ContentBrowserModule.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"

TArray<FString> UZspcCpp::GetSelectedFolders()
{
	TArray<FString> Folders;
	FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
	IContentBrowserSingleton& ContentBrowserSingleton = ContentBrowserModule.Get();
	ContentBrowserSingleton.GetSelectedFolders(Folders);
	return Folders;
}

TArray<FString> UZspcCpp::GetSubFoldersRecursive(const FString Filepath)
{
	TArray<FString> Subfolders = TArray<FString>();
	FString FinalPath = Filepath / TEXT("/*");
	IFileManager& FileManager = IFileManager::Get();
	FileManager.FindFiles(Subfolders, *FinalPath, false, true);
	TArray<FString> SubfoldersCopy = Subfolders;
	for (FString CurrentFolder : SubfoldersCopy)
	{
		Subfolders += GetSubFoldersRecursive(Filepath + "/" + CurrentFolder);
	}
	return Subfolders;
}

TArray<FString> UZspcCpp::GetSubFoldersPathsRecursive(const FString Filepath)
{
	TArray<FString> Subfolders = TArray<FString>();

	FString FinalPath = Filepath / TEXT("/*");
	IFileManager& FileManager = IFileManager::Get();
	FileManager.FindFiles(Subfolders, *FinalPath, false, true);

	TArray<FString> Subfolders_p = Subfolders;

	for (int32 index = 0; index != Subfolders.Num(); ++ index)
	{
		Subfolders_p[index] = Filepath + "/" + Subfolders[index];
	}

	TArray<FString> Subfolders_pCopy = Subfolders_p;

	for (FString Path_p : Subfolders_pCopy)
	{
		//UE_LOG(LogTemp, Warning, TEXT("Path: %s"), *Path_p);
		FString LString;
		FString RString;
		Path_p.Split("/", &LString, &RString, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
		Subfolders_p += GetSubFoldersPathsRecursive(Filepath + "/" + RString);
	}

	return Subfolders_p;
}

TArray<FString> UZspcCpp::GetSubFolders(const FString Filepath)
{
	TArray<FString> Subfolders = TArray<FString>();
	FString FinalPath = Filepath / TEXT("/*");
	IFileManager& FileManager = IFileManager::Get();
	FileManager.FindFiles(Subfolders, *FinalPath, false, true);

	return Subfolders;
}

TArray<FString> UZspcCpp::GetSubFoldersPathsOfSelectedFolders()
{
	TArray<FString> AllSubFolders = TArray<FString>();
	for (FString SelectedFolder : GetSelectedFolders())
	{
		FString LString;
		FString RString;
		FString ProjectPath;
		FString ProjectFileName;
		FString ProjectExtension;
		SelectedFolder.Split("/Game/", &LString, &RString, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
		FPaths::Split(FPaths::GetProjectFilePath(), ProjectPath, ProjectFileName, ProjectExtension);
		FString SubFolderPath = ProjectPath + "/Content/" + RString;
		AllSubFolders += GetSubFoldersPathsRecursive(SubFolderPath);
		
	}
	return AllSubFolders;
}

TArray<FString> UZspcCpp::GetSubFoldersOfSelectedFolders()
{
	TArray<FString> AllSubFolders = TArray<FString>();
	for (FString SelectedFolder : GetSelectedFolders())
	{
		FString LString;
		FString RString;
		FString ProjectPath;
		FString ProjectFileName;
		FString ProjectExtension;
		SelectedFolder.Split("/Game/", &LString, &RString, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
		FPaths::Split(FPaths::GetProjectFilePath(), ProjectPath, ProjectFileName, ProjectExtension);
		FString SubFolderPath = ProjectPath + "/Content/" + RString;
		AllSubFolders += GetSubFoldersRecursive(SubFolderPath);

	}
	return AllSubFolders;
}

FString UZspcCpp::DiskPathToGamePath(const FString DiskPath)
{
	FString ProjectPath;
	FString ProjectFileName;
	FString ProjectExtension;
	FPaths::Split(FPaths::GetProjectFilePath(), ProjectPath, ProjectFileName, ProjectExtension);
	FString ProjectPathContent = ProjectPath + "/Content/";
	FString LString;
	FString RString;
	DiskPath.Split(ProjectPathContent, &LString, &RString, ESearchCase::IgnoreCase, ESearchDir::FromStart);
	FString GamePath = "/Game/" + RString;
	return GamePath;
}

//bool UMusicalRangeBPFunctionLibrary::LoadFromFileGetAvailableFolders(TArray<FString>& Folders, FString FullFilePath, bool printFolders) {
//	FPaths::NormalizeDirectoryName(FullFilePath);
//	IFileManager& FileManager = IFileManager::Get();
//
//	FString FinalPath = FullFilePath / TEXT("*");
//	FileManager.FindFiles(Folders, *FinalPath, false, true);
//
//	if (printFolders)
//	{
//		for (int i = 0; i < Folders.Num(); i++)
//		{
//			UE_LOG(LogMusicalRange, Log, TEXT("File Found: %s"), *Folders[i]);
//		}
//	}
//	return true;
//}