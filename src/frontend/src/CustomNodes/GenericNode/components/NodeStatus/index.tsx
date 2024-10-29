import { getSpecificClassFromBuildStatus } from "@/CustomNodes/helpers/get-class-from-build-status";
import useIconStatus from "@/CustomNodes/hooks/use-icons-status";
import useUpdateValidationStatus from "@/CustomNodes/hooks/use-update-validation-status";
import useValidationStatusString from "@/CustomNodes/hooks/use-validation-status-string";
import ShadTooltip from "@/components/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import {
  ICON_STROKE_WIDTH,
  RUN_TIMESTAMP_PREFIX,
  STATUS_BUILD,
  STATUS_BUILDING,
  STATUS_INACTIVE,
  TOOLTIP_OUTDATED_NODE,
} from "@/constants/constants";
import { BuildStatus } from "@/constants/enums";
import { track } from "@/customization/utils/analytics";
import { useDarkStore } from "@/stores/darkStore";
import useFlowStore from "@/stores/flowStore";
import { useShortcutsStore } from "@/stores/shortcuts";
import { VertexBuildTypeAPI } from "@/types/api";
import { NodeDataType } from "@/types/flow";
import { findLastNode } from "@/utils/reactflowUtils";
import { classNames } from "@/utils/utils";
import { Check } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import IconComponent from "../../../../components/genericIconComponent";

export default function NodeStatus({
  nodeId,
  display_name,
  selected,
  setBorderColor,
  frozen,
  showNode,
  data,
  buildStatus,
  isOutdated,
  isUserEdited,
  handleUpdateCode,
  loadingUpdate,
}: {
  nodeId: string;
  display_name: string;
  selected: boolean;
  setBorderColor: (color: string) => void;
  frozen?: boolean;
  showNode: boolean;
  data: NodeDataType;
  buildStatus: BuildStatus;
  isOutdated: boolean;
  isUserEdited: boolean;
  handleUpdateCode: () => void;
  loadingUpdate: boolean;
}) {
  const nodeId_ = data.node?.flow?.data
    ? (findLastNode(data.node?.flow.data!)?.id ?? nodeId)
    : nodeId;
  const [validationString, setValidationString] = useState<string>("");
  const [validationStatus, setValidationStatus] =
    useState<VertexBuildTypeAPI | null>(null);

  const conditionSuccess =
    buildStatus === BuildStatus.BUILT ||
    (!(!buildStatus || buildStatus === BuildStatus.TO_BUILD) &&
      validationStatus &&
      validationStatus.valid);

  const lastRunTime = useFlowStore(
    (state) => state.flowBuildStatus[nodeId_]?.timestamp,
  );
  const iconStatus = useIconStatus(buildStatus);
  const buildFlow = useFlowStore((state) => state.buildFlow);
  const isBuilding = useFlowStore((state) => state.isBuilding);
  const setNode = useFlowStore((state) => state.setNode);
  const version = useDarkStore((state) => state.version);

  function handlePlayWShortcut() {
    if (buildStatus === BuildStatus.BUILDING || isBuilding || !selected) return;
    setValidationStatus(null);
    buildFlow({ stopNodeId: nodeId });
  }

  const play = useShortcutsStore((state) => state.play);
  const flowPool = useFlowStore((state) => state.flowPool);
  useHotkeys(play, handlePlayWShortcut, { preventDefault: true });
  useValidationStatusString(validationStatus, setValidationString);
  useUpdateValidationStatus(nodeId_, flowPool, setValidationStatus);

  const getBaseBorderClass = (selected) => {
    let className =
      selected && !isBuilding
        ? " border-[1.5px] border-foreground hover:shadow-node"
        : "border-[1.5px] hover:shadow-node";
    let frozenClass = selected ? "border-ring-frozen" : "border-frozen";
    return frozen ? frozenClass : className;
  };

  const getNodeBorderClassName = (
    selected: boolean,
    showNode: boolean,
    buildStatus: BuildStatus | undefined,
    validationStatus: VertexBuildTypeAPI | null,
  ) => {
    const specificClassFromBuildStatus = getSpecificClassFromBuildStatus(
      buildStatus,
      validationStatus,
      isBuilding,
    );

    const baseBorderClass = getBaseBorderClass(selected);
    const names = classNames(baseBorderClass, specificClassFromBuildStatus);
    return names;
  };

  useEffect(() => {
    setBorderColor(
      getNodeBorderClassName(selected, showNode, buildStatus, validationStatus),
    );
  }, [selected, showNode, buildStatus, validationStatus, frozen]);

  useEffect(() => {
    if (buildStatus === BuildStatus.BUILT && !isBuilding) {
      setNode(
        nodeId,
        (old) => {
          return {
            ...old,
            data: {
              ...old.data,
              node: {
                ...old.data.node,
                lf_version: version,
              },
            },
          };
        },
        false,
      );
    }
  }, [buildStatus, isBuilding]);

  const divRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const runClass = "justify-left flex font-normal text-muted-foreground";

  const handleClickRun = () => {
    if (buildStatus === BuildStatus.BUILDING || isBuilding) return;
    setValidationStatus(null);
    buildFlow({ stopNodeId: nodeId });
    track("Flow Build - Clicked", { stopNodeId: nodeId });
  };

  return (
    <>
      <div className="flex flex-shrink-0 items-center gap-1">
        {isOutdated && !isUserEdited && (
          <ShadTooltip content={TOOLTIP_OUTDATED_NODE}>
            <Button
              onClick={handleUpdateCode}
              unstyled
              className={"hit-area-icon button-run-bg group p-1"}
              loading={loadingUpdate}
            >
              <IconComponent
                name="AlertTriangle"
                className="icon-size text-placeholder-foreground group-hover:fill-status-yellow group-hover:text-foreground"
              />
            </Button>
          </ShadTooltip>
        )}
        <ShadTooltip
          content={
            buildStatus === BuildStatus.BUILDING ? (
              <span> {STATUS_BUILDING} </span>
            ) : buildStatus === BuildStatus.INACTIVE ? (
              <span> {STATUS_INACTIVE} </span>
            ) : !validationStatus ? (
              <span className="flex">{STATUS_BUILD}</span>
            ) : (
              <div className="max-h-100 p-2">
                <div className="max-h-80 overflow-auto">
                  {validationString && (
                    <div className="ml-1 pb-2 text-status-red">
                      {validationString}
                    </div>
                  )}
                  {lastRunTime && (
                    <div className={runClass}>
                      <div>{RUN_TIMESTAMP_PREFIX}</div>
                      <div className="ml-1 text-status-blue">{lastRunTime}</div>
                    </div>
                  )}
                </div>
                <div className={runClass}>
                  <div>Duration:</div>
                  <div className="ml-1 text-status-blue">
                    {validationStatus?.data.duration}
                  </div>
                </div>
              </div>
            )
          }
          side="bottom"
        >
          <div className="cursor-help">
            {conditionSuccess ? (
              <div className="mr-1 flex gap-1 rounded-sm bg-emerald-50 px-1 font-jetbrains text-[11px] font-bold text-emerald-500">
                <Check className="h-4 w-4 items-center self-center" />
                <span>
                  {validationStatus?.data?.duration?.replace(" ", "")}
                </span>
              </div>
            ) : (
              iconStatus
            )}
          </div>
        </ShadTooltip>

        <ShadTooltip content={"Run component"} contrastTooltip>
          <div
            ref={divRef}
            className="button-run-bg hit-area-icon"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={handleClickRun}
          >
            {showNode && (
              <Button unstyled className="group">
                <div data-testid={`button_run_` + display_name.toLowerCase()}>
                  <IconComponent
                    name="Play"
                    className={`play-button-icon ${
                      isHovered
                        ? "text-foreground"
                        : "text-placeholder-foreground"
                    }`}
                    strokeWidth={ICON_STROKE_WIDTH}
                  />
                </div>
              </Button>
            )}
          </div>
        </ShadTooltip>
      </div>
    </>
  );
}
