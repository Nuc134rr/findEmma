// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ZspcCpp.generated.h"

/**
 * 
 */
UCLASS()
class FINDEMMATEST_API UZspcCpp : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSubFoldersPathsOfSelectedFolders();

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSubFoldersOfSelectedFolders();

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static FString DiskPathToGamePath(const FString DiskPath);

private:
	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSelectedFolders();

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSubFoldersPathsRecursive(const FString Filepath);

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSubFoldersRecursive(const FString Filepath);

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
	static TArray<FString> GetSubFolders(const FString Filepath);

};