import { AddFolderType } from "@/pages/MainPage/entities";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useFolderStore } from "@/stores/foldersStore";
import { Users, useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

interface IPostAddFolders {
  data: AddFolderType;
}

export const usePostFolders: useMutationFunctionType<
  undefined,
  IPostAddFolders
> = (options?) => {
  const { mutate } = UseRequestProcessor();

  const addFoldersFn = async (newFolder: IPostAddFolders): Promise<void> => {
    const payload = {
      name: newFolder.data.name,
      description: newFolder.data.description,
      flows_list: newFolder.data.flows ?? [],
      components_list: newFolder.data.components ?? [],
    };

    const res = await api.post(`${getURL("FOLDERS")}/`, payload);
    await useFolderStore.getState().getFoldersApi(true);
    return res.data;
  };

  const mutation = mutate(["usePostFolders"], addFoldersFn, options);

  return mutation;
};
