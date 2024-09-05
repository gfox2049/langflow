import useFlowStore from "@/stores/flowStore";
import IconComponent from "../../../../../../../components/genericIconComponent";
import { Button } from "../../../../../../../components/ui/button";
import { Case } from "../../../../../../../shared/components/caseComponent";
import { FilePreviewType } from "../../../../../../../types/components";
import { classNames } from "../../../../../../../utils/utils";

const BUTTON_STATES = {
  NO_INPUT: "bg-high-indigo text-background",
  HAS_CHAT_VALUE: "text-primary",
  SHOW_STOP: "bg-error text-background cursor-pointer",
  DEFAULT: "bg-chat-send text-background",
};

type ButtonSendWrapperProps = {
  send: () => void;
  lockChat: boolean;
  noInput: boolean;
  chatValue: string;
  files: FilePreviewType[];
};

const ButtonSendWrapper = ({
  send,
  lockChat,
  noInput,
  chatValue,
  files,
}: ButtonSendWrapperProps) => {
  const stopBuilding = useFlowStore((state) => state.stopBuilding);

  const isBuilding = useFlowStore((state) => state.isBuilding);
  const showStopButton = lockChat || files.some((file) => file.loading);
  const showPlayButton = !lockChat && noInput;
  const showSendButton =
    !(lockChat || files.some((file) => file.loading)) && !noInput;

  const baseClass = "form-modal-send-button";

  const getConditionalClasses = () => {
    if (noInput) return BUTTON_STATES.NO_INPUT;
    if (chatValue) return BUTTON_STATES.HAS_CHAT_VALUE;
    if (showStopButton) return BUTTON_STATES.SHOW_STOP;
    return BUTTON_STATES.DEFAULT;
  };

  const buttonClasses = classNames(baseClass, getConditionalClasses());

  const handleClick = () => {
    if (!showStopButton) {
      send();
      return;
    }

    if (showStopButton && isBuilding) {
      stopBuilding();
      return;
    }
  };

  return (
    <Button
      className={buttonClasses}
      disabled={lockChat && !isBuilding}
      onClick={handleClick}
      unstyled
    >
      <Case condition={showStopButton}>
        <IconComponent
          name="Square"
          className="form-modal-lock-icon"
          aria-hidden="true"
        />
      </Case>

      <Case condition={showPlayButton}>
        <IconComponent
          name="Zap"
          className="form-modal-play-icon"
          aria-hidden="true"
        />
      </Case>

      <Case condition={showSendButton}>
        <IconComponent
          name="LucideSend"
          className="form-modal-send-icon"
          aria-hidden="true"
        />
      </Case>
    </Button>
  );
};

export default ButtonSendWrapper;
