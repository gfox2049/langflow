import ForwardedIconComponent from "@/components/genericIconComponent";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useMobile } from "@/hooks/use-mobile";
import { cn } from "@/utils/utils";
import { NavProps } from "../../../../types/templates/types";

export function Nav({ categories, currentTab, setCurrentTab }: NavProps) {
  const isMobile = useMobile();

  return (
    <Sidebar collapsible={isMobile ? "icon" : "none"}>
      <SidebarContent className="gap-0 p-2">
        <div
          className={cn("relative flex items-center gap-2 px-2 py-3 md:px-4")}
          data-testid="modal-title"
        >
          <SidebarTrigger
            className={cn(
              "flex h-8 shrink-0 items-center rounded-md text-lg font-semibold leading-none tracking-tight text-primary outline-none ring-ring transition-[margin,opa] duration-200 ease-linear focus-visible:ring-1 md:hidden [&>svg]:size-4 [&>svg]:shrink-0",
            )}
          />
          <div
            className={cn(
              "flex h-8 shrink-0 items-center rounded-md text-lg font-semibold leading-none tracking-tight text-primary outline-none ring-ring transition-[margin,opa] duration-200 ease-linear focus-visible:ring-1 [&>svg]:size-4 [&>svg]:shrink-0",
              "group-data-[collapsible=icon]:-mt-8 group-data-[collapsible=icon]:opacity-0",
            )}
          >
            Categories
          </div>
        </div>

        {categories.map((category, index) => (
          <SidebarGroup key={index}>
            <SidebarGroupLabel
              className={`${
                index === 0
                  ? "hidden"
                  : "mb-1 text-sm font-semibold text-muted-foreground"
              }`}
            >
              {category.title}
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {category.items.map((link) => (
                  <SidebarMenuItem key={link.id}>
                    <SidebarMenuButton
                      tabIndex={1}
                      onClick={() => setCurrentTab(link.id)}
                      isActive={currentTab === link.id}
                      data-testid={`side_nav_options_${link.title.toLowerCase().replace(/\s+/g, "_")}`}
                    >
                      <ForwardedIconComponent
                        name={link.icon}
                        className={`mr-2 h-4 w-4 stroke-2 ${
                          currentTab === link.id
                            ? "x-gradient"
                            : "text-muted-foreground"
                        }`}
                      />
                      <span>{link.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
    </Sidebar>
  );
}
