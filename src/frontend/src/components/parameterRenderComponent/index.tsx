import { handleOnNewValueType } from "@/CustomNodes/hooks/use-handle-new-value";
import { TEXT_FIELD_TYPES } from "@/constants/constants";
import { APIClassType, InputFieldType } from "@/types/api";
import { useMemo } from "react";
import TableNodeComponent from "./components/TableNodeComponent";
import CodeAreaComponent from "./components/codeAreaComponent";
import DictComponent from "./components/dictComponent";
import FloatComponent from "./components/floatComponent";
import InputFileComponent from "./components/inputFileComponent";
import IntComponent from "./components/intComponent";
import KeypairListComponent from "./components/keypairListComponent";
import LinkComponent from "./components/linkComponent";
import PromptAreaComponent from "./components/promptComponent";
import ToggleShadComponent from "./components/toggleShadComponent";
import { RefreshParameterComponent } from "./components/refreshParameterComponent";
import { StrRenderComponent } from "./components/strRenderComponent";
import { EmptyParameterComponent } from "./components/emptyParameterComponent";
import { InputProps } from "./types";
import InputListComponent from "./components/inputListComponent";

export function ParameterRenderComponent({
  handleOnNewValue,
  name,
  nodeId,
  templateData,
  templateValue,
  editNode,
  handleNodeClass,
  nodeClass,
  disabled,
}: {
  handleOnNewValue: handleOnNewValueType;
  name: string;
  nodeId: string;
  templateData: Partial<InputFieldType>;
  templateValue: any;
  editNode: boolean;
  handleNodeClass: (value: any, code?: string, type?: string) => void;
  nodeClass: APIClassType;
  disabled: boolean;
}) {
  const onChange = (value: any) => {
    handleOnNewValue({ value });
  };

  const id = (
    templateData.type +
    "_" +
    (editNode ? "edit_" : "") +
    templateData.name
  ).toLowerCase();

  const renderComponent = ():React.ReactElement<InputProps> => {
    const baseInputProps: InputProps = {
    id,
    value: templateValue,
    editNode,
    handleOnNewValue,
    disabled,
    nodeClass,
    handleNodeClass,
    readonly: templateData.readonly,
    };
    if (TEXT_FIELD_TYPES.includes(templateData.type ?? "")) {
      if(templateData.listist) {
        return (
          <InputListComponent
            {...baseInputProps}
            componentName={name}
            id={`inputlist_${id}`}
          />
        );
      }
      return (
        <StrRenderComponent
          {...baseInputProps}
          templateData={templateData}
          value={templateValue}
          name={name}
          disabled={disabled}
          handleOnNewValue={handleOnNewValue}
          id={id}
          editNode={editNode}
        />
      );
    }
    switch (templateData.type) {
      case "NestedDict":
        return (
          <DictComponent
            {...baseInputProps}
            id={`dict_${id}`}
          />
        );
      case "dict":
        return (
          <KeypairListComponent
            {...baseInputProps}
            isList={templateData.list ?? false}
            id={`keypair_${id}`}
          />
        );
      case "bool":
        return (
          <ToggleShadComponent
          {...baseInputProps}
          id={`toggle_${id}`}
          />
        );
      case "link":
        return (
          <LinkComponent
            {...baseInputProps}
            icon={templateData.icon}
            text={templateData.text}
            id={`link_${id}`}
          />
        );
      case "float":
        return (
          <FloatComponent
            {...baseInputProps}
            id={`float_${id}`}
            rangeSpec={templateData.range_spec}
          />
        );
      case "int":
        return (
          <IntComponent
          {...baseInputProps}
          rangeSpec={templateData.range_spec}
          id={`int_${id}`}
          />
        );
      case "file":
        return (
          <InputFileComponent
            {...baseInputProps}
            fileTypes={templateData.fileTypes}
            id={`inputfile_${id}`}
          />
        );
      case "prompt":
        return (
          <PromptAreaComponent
          {...baseInputProps}
          readonly={!!nodeClass.flow}
          field_name={name}
          id={`promptarea_${id}`}
          />
        );
      case "code":
        return (
          <CodeAreaComponent
            {...baseInputProps}
            id={`codearea_${id}`}
          />
        );
      case "table":
        return (
          <TableNodeComponent
            {...baseInputProps}
            description={templateData.info || "Add or edit data"}
            columns={templateData?.table_schema?.columns}
            tableTitle={templateData?.display_name ?? "Table"}
          />
        );
      default:
        return (
          <EmptyParameterComponent
            {...baseInputProps}
          />
        );
    }
  };

  return useMemo(
    () => (
      <RefreshParameterComponent
        templateData={templateData}
        disabled={disabled}
        nodeId={nodeId}
        editNode={editNode}
        nodeClass={nodeClass}
        handleNodeClass={handleNodeClass}
        name={name}
      >
        {renderComponent()}
      </RefreshParameterComponent>
    ),
    [templateData, disabled, nodeId, editNode, nodeClass, name, templateValue],
  );
}
