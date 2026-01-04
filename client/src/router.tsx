import {
  createRouter,
  createRootRoute,
  createRoute,
} from "@tanstack/react-router";
import { RootLayout } from "./pages/RootLayout";
import { HomePage } from "./pages/HomePage";
import { AlarmsPage } from "./pages/AlarmsPage";
import { AlarmEditPage } from "./pages/AlarmEditPage";
const rootRoute = createRootRoute({
  component: RootLayout,
});
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: HomePage,
});
const alarmsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/alarms",
  component: AlarmsPage,
});
const alarmNewRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/alarms/new",
  component: AlarmEditPage,
});
const alarmEditRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/alarms/$alarmId",
  component: AlarmEditPage,
});
const routeTree = rootRoute.addChildren([
  indexRoute,
  alarmsRoute,
  alarmNewRoute,
  alarmEditRoute,
]);
export const router = createRouter({ routeTree });
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
