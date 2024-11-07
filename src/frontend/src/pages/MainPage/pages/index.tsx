import CardsWrapComponent from "@/components/cardsWrapComponent";
import SideBarFoldersButtonsComponent from "@/components/folderSidebarComponent/components/sideBarFolderButtons";
import LoadingComponent from "@/components/loadingComponent";
import { SidebarProvider } from "@/components/ui/sidebar";
import { useDeleteFolders } from "@/controllers/API/queries/folders";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import useAlertStore from "@/stores/alertStore";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useFolderStore } from "@/stores/foldersStore";
import { useIsFetching, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import useFileDrop from "../hooks/use-on-file-drop";
import ModalsComponent from "../oldComponents/modalsComponent";
import EmptyPage from "./emptyPage";

export default function CollectionPage(): JSX.Element {
  const [openModal, setOpenModal] = useState(false);
  const [openDeleteFolderModal, setOpenDeleteFolderModal] = useState(false);
  const setFolderToEdit = useFolderStore((state) => state.setFolderToEdit);
  const navigate = useCustomNavigate();
  const flows = useFlowsManagerStore((state) => state.flows);
  const examples = useFlowsManagerStore((state) => state.examples);
  const handleFileDrop = useFileDrop("flow");
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const folderToEdit = useFolderStore((state) => state.folderToEdit);
  const folders = useFolderStore((state) => state.folders);
  const queryClient = useQueryClient();
  const isPendingFolders = !!useIsFetching({
    queryKey: ["useGetFolders"],
    exact: false,
  });

  useEffect(() => {
    return () => queryClient.removeQueries({ queryKey: ["useGetFolder"] });
  }, []);

  const { mutate } = useDeleteFolders();

  const handleDeleteFolder = () => {
    mutate(
      {
        folder_id: folderToEdit?.id!,
      },
      {
        onSuccess: () => {
          setSuccessData({
            title: "Folder deleted successfully.",
          });
          navigate("/all");
        },
        onError: (err) => {
          console.error(err);
          setErrorData({
            title: "Error deleting folder.",
          });
        },
      },
    );
  };

  return (
    <SidebarProvider>
      {(flows?.length !== examples?.length || folders?.length > 1) && (
        <SideBarFoldersButtonsComponent
          handleChangeFolder={(id: string) => {
            navigate(`all/folder/${id}`);
          }}
          handleDeleteFolder={(item) => {
            setFolderToEdit(item);
            setOpenDeleteFolderModal(true);
          }}
        />
      )}
      <main className="flex flex-1">
        {!isPendingFolders ? (
          <div className={`relative mx-auto h-full w-full overflow-y-scroll`}>
            <CardsWrapComponent
              onFileDrop={handleFileDrop}
              dragMessage={`Drop your file(s) here`}
            >
              {flows?.length !== examples?.length || folders?.length > 1 ? (
                <Outlet />
              ) : (
                <EmptyPage setOpenModal={setOpenModal} />
              )}
            </CardsWrapComponent>
          </div>
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <LoadingComponent remSize={30} />
          </div>
        )}
      </main>
      <ModalsComponent
        openModal={openModal}
        setOpenModal={setOpenModal}
        openDeleteFolderModal={openDeleteFolderModal}
        setOpenDeleteFolderModal={setOpenDeleteFolderModal}
        handleDeleteFolder={handleDeleteFolder}
      />
    </SidebarProvider>
  );
}
