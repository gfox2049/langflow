import useAlertStore from "@/stores/alertStore";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useTypesStore } from "@/stores/typesStore";
import { useMutationFunctionType } from "@/types/api";
import { FlowType, PaginatedFlowsType } from "@/types/flow";
import {
  extractFieldsFromComponenents,
  processFlows,
} from "@/utils/reactflowUtils";
import { UseMutationOptions } from "@tanstack/react-query";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

interface GetFlowsParams {
  components_only?: boolean;
  get_all?: boolean;
  header_flows?: boolean;
  folder_id?: string;
  remove_example_flows?: boolean;
  page?: number;
  size?: number;
}

const addQueryParams = (url: string, params: GetFlowsParams): string => {
  const queryParams = new URLSearchParams();
  if (params.components_only) queryParams.append("components_only", "true");
  if (params.get_all) queryParams.append("get_all", "true");
  if (params.header_flows) queryParams.append("header_flows", "true");
  if (params.folder_id) queryParams.append("folder_id", params.folder_id);
  if (params.remove_example_flows)
    queryParams.append("remove_example_flows", "true");
  if (params.page) queryParams.append("page", params.page.toString());
  if (params.size) queryParams.append("size", params.size.toString());
  const queryString = queryParams.toString();
  return queryString ? `${url}?${queryString}` : url;
};

export const useGetRefreshFlows: useMutationFunctionType<
  undefined,
  GetFlowsParams
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const setFlows = useFlowsManagerStore((state) => state.setFlows);
  const setErrorData = useAlertStore((state) => state.setErrorData);

  const getRefreshFlowsFn = async (
    params: GetFlowsParams,
  ): Promise<FlowType[] | PaginatedFlowsType> => {
    const url = addQueryParams(`${getURL("FLOWS")}/`, params);
    const { data } = await api.get<FlowType[]>(url);
    return data;
  };

  const mutationFn = async (
    params?: GetFlowsParams,
  ): Promise<FlowType[] | PaginatedFlowsType> => {
    try {
      await getRefreshFlowsFn(params!).then(async (dbDataFlows) => {
        const dbDataComponents = await getRefreshFlowsFn({
          components_only: true,
          get_all: true,
        });

        if (dbDataComponents) {
          const { data } = processFlows(dbDataComponents as FlowType[]);
          useTypesStore.setState((state) => ({
            data: { ...state.data, ["saved_components"]: data },
            ComponentFields: extractFieldsFromComponenents({
              ...state.data,
              ["saved_components"]: data,
            }),
          }));
        }

        if (dbDataFlows) {
          const flows = Array.isArray(dbDataFlows)
            ? dbDataFlows
            : dbDataFlows.items;

          setFlows(flows);
          return flows;
        }
      });

      return [];
    } catch (e) {
      setErrorData({
        title: "Could not load flows from database",
      });
      throw e;
    }
  };

  const mutation = mutate(["useGetRefreshFlows"], mutationFn, {
    ...(options as UseMutationOptions<any, any, void, unknown>),
  });

  return mutation;
};
