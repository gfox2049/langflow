import useFlowStore from "@/stores/flowStore";
import { NodeType } from "@/types/flow";
import { useUpdateNodeInternals } from "@xyflow/react";
import { cloneDeep } from "lodash";

const useHandleNodeClass = (
  nodeId: string,
  setMyNode?: (
    id: string,
    update: NodeType | ((oldState: NodeType) => NodeType),
  ) => void,
) => {
  const setNode = setMyNode ?? useFlowStore((state) => state.setNode);
  const updateNodeInternals = useUpdateNodeInternals();

  const handleNodeClass = (newNodeClass, type?: string) => {
    setNode(nodeId, (oldNode) => {
      let newNode = cloneDeep(oldNode);

      newNode.data = {
        ...newNode.data,
        node: cloneDeep(newNodeClass),
      };
      if (type) {
        newNode.data.type = type;
      }

      updateNodeInternals(nodeId);

      return newNode;
    });
  };

  return { handleNodeClass };
};

export default useHandleNodeClass;
