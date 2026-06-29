# Android-to-ArkTS Conversion Skill

## Overview
This skill documents the systematic process of converting an Android (Java/Kotlin) project to HarmonyOS ArkTS syntax. It covers mapping rules, patterns, and conversion examples based on the AntennaPod project conversion.

## Conversion Mapping Rules

### 1. Language & Type System

| Android (Java) | ArkTS | Notes |
|---|---|---|
| `class Foo { }` | `class Foo { }` | Similar syntax, but ArkTS is TypeScript-based |
| `int`, `long`, `float`, `double` | `number` | ArkTS uses unified `number` type |
| `boolean` | `boolean` | Same |
| `String` | `string` | Lowercase in ArkTS |
| `List<T>` | `Array<T>` or `T[]` | ArkTS uses TypeScript arrays |
| `Map<K,V>` | `Map<K,V>` or `Record<K,V>` | Both available |
| `Set<T>` | `Set<T>` | Same |
| `ArrayList<T>` | `Array<T>` | No ArrayList in ArkTS |
| `HashMap<K,V>` | `Map<K,V>` | Use Map instead |
| `null` | `null` or `undefined` | Both exist in ArkTS |
| `@Nullable` | `type \| null` | Union type |
| `@NonNull` | Just the type | Non-null is default |
| `Serializable` | Use JSON serialization | No direct equivalent |
| `Parcelable` | Use JSON serialization | No direct equivalent |
| `interface Foo { }` | `interface Foo { }` | Same syntax |
| `abstract class` | `abstract class` | Same |
| `extends` | `extends` | Same |
| `implements` | `implements` | Same |
| `@Override` | No decorator needed | Methods override by default |
| `static` | `static` | Same |
| `final` | `readonly` or `const` | For properties use readonly |
| `enum` | `enum` | Same but TypeScript style |
| `throws Exception` | No checked exceptions | Use try/catch |

### 2. Android Component → ArkTS Component Mapping

| Android Component | ArkTS Equivalent | Notes |
|---|---|---|
| `Activity` | `@Entry @Component` | Main page entry |
| `Fragment` | `@Component` | Reusable component |
| `Service` | `ServiceExtensionAbility` | Background service |
| `BroadcastReceiver` | `CommonEventSubscriber` | System event listener |
| `ContentProvider` | No direct equivalent | Use distributed data or RDB |
| `Application` | `AbilityStage` | App lifecycle |
| `ViewModel` | `@State` + custom class | Or use AppStorage |
| `LiveData` | `@State` / `@Link` / `@Prop` | Reactive state |
| `RecyclerView` | `List` component | Declarative list |
| `Adapter` | LazyForEach data source | For list rendering |
| `ViewHolder` | `@Builder` function | Item template |
| `SharedPreferences` | `data_preferences` | Preferences API |
| `SQLite/Room` | `@ohos.data.relationalStore` | RDB store |
| `WorkManager` | `workScheduler` | Background tasks |
| `Intent` | `Want` | Navigation & data passing |
| `Bundle` | `Want` params or JSON | Data passing |
| `Context` | `this` (in Ability/Extension) | Context available on ability |
| `Resources` | `$r('app.string.xxx')` | Resource reference |
| `XML Layout` | Declarative UI code | No XML layouts in ArkTS |
| `AndroidManifest.xml` | `module.json5` | Module configuration |
| `build.gradle` | `build-profile.json5` | Build configuration |

### 3. UI Component Mapping

| Android XML/Widget | ArkTS Component | Notes |
|---|---|---|
| `TextView` | `Text()` | Declarative |
| `EditText` | `TextInput()` | Declarative |
| `ImageView` | `Image()` | Declarative |
| `Button` | `Button()` | Declarative |
| `LinearLayout(V)` | `Column()` | Vertical layout |
| `LinearLayout(H)` | `Row()` | Horizontal layout |
| `FrameLayout` | `Stack()` | Overlay layout |
| `RelativeLayout` | `RelativeContainer()` | Relative positioning |
| `ConstraintLayout` | `RelativeContainer()` + constraints | |
| `ScrollView` | `Scroll()` | Scrollable container |
| `RecyclerView` | `List()` + `ForEach`/`LazyForEach` | Lazy list |
| `ViewPager2` | `Swiper()` | Swipe pages |
| `ProgressBar` | `Progress()` | Progress indicator |
| `Switch` | `Toggle()` | Toggle switch |
| `CheckBox` | `Checkbox()` | Checkbox |
| `RadioButton` | `Radio()` | Radio button |
| `Spinner` | `Select()` | Dropdown |
| `Toolbar` | No direct equiv, use `Row()` | Custom toolbar |
| `BottomNavigationView` | `Tabs()` | Bottom tabs |
| `DrawerLayout` | `SideBarContainer()` | Side drawer |
| `Dialog` | `CustomDialogController` | Dialog |
| `Toast` | `promptAction.showToast()` | Toast message |
| `Snackbar` | `promptAction.showDialog()` | Similar to snackbar |
| `WebView` | `Web()` | Web component |
| `VideoView` | `Video()` | Video player |
| `SurfaceView` | `XComponent()` | Surface rendering |

### 4. Layout Attributes Mapping

| Android XML Attribute | ArkTS Attribute | Notes |
|---|---|---|
| `android:layout_width` | `.width()` | Method chain |
| `android:layout_height` | `.height()` | Method chain |
| `android:padding` | `.padding()` | Method chain |
| `android:margin` | `.margin()` | Method chain |
| `android:background` | `.backgroundColor()` | Method chain |
| `android:text` | `Text('content')` | Constructor param |
| `android:textSize` | `.fontSize()` | Method chain |
| `android:textColor` | `.fontColor()` | Method chain |
| `android:visibility` | `.visibility()` / `.opacity()` | Visibility |
| `android:onClick` | `.onClick(() => {})` | Event handler |
| `android:orientation` | Use `Column` or `Row` | Layout direction |
| `android:gravity` | `.align()` / `.alignItems()` | Alignment |
| `android:layout_weight` | `.layoutWeight()` | Weight |
| `android:src` | `Image($r('app.media.xxx'))` | Image source |
| `android:contentDescription` | `.accessibilityText()` | Accessibility |
| `android:elevation` | `.shadow()` | Shadow |

### 5. Lifecycle Mapping

| Android Lifecycle | ArkTS Lifecycle | Notes |
|---|---|---|
| `onCreate()` | `aboutToAppear()` | Component creation |
| `onStart()` | `onPageShow()` | Page visible |
| `onResume()` | `onPageShow()` | Page interactive |
| `onPause()` | `onPageHide()` | Page background |
| `onStop()` | `onPageHide()` | Page hidden |
| `onDestroy()` | `aboutToDisappear()` | Component destruction |
| `onSaveInstanceState()` | No direct equiv | Use AppStorage |
| `onActivityResult()` | `abilityContext.startAbilityForResult()` callback | |

### 6. Navigation Mapping

| Android Navigation | ArkTS Navigation | Notes |
|---|---|---|
| `startActivity(Intent)` | `router.pushUrl()` or `Navigation.pushPath()` | Page navigation |
| `finish()` | `router.back()` or `Navigation.pop()` | Go back |
| `FragmentTransaction.replace()` | `Navigation.replacePath()` | Replace content |
| `FragmentTransaction.add()` | Stack-based navigation | Navigation stack |
| `Intent.putExtra()` | `router.pushUrl({params: {}})` | Pass data |
| `getIntent().getXxxExtra()` | `router.getParams()` | Get data |
| Deep Links | `router.pushUrl()` with URL scheme | |

### 7. Networking Mapping

| Android (OkHttp) | ArkTS (@ohos.net.http) | Notes |
|---|---|---|
| `OkHttpClient` | `http.createHttp()` | HTTP client |
| `Request.Builder()` | `http.request(url, {method})` | Build request |
| `Response` | `HttpResponse` | Response object |
| `ResponseBody.string()` | `response.result` | Get body |
| Interceptors | Custom wrapper | No direct equiv |

### 8. Database Mapping

| Android (SQLite/Room) | ArkTS (RDB) | Notes |
|---|---|---|
| `SQLiteOpenHelper` | `dataRdb.getRdbStore()` | Database helper |
| `ContentValues` | `dataRdb.ValuesBucket` | Row values |
| `Cursor` | `ResultSet` | Query results |
| `@Dao` | Custom wrapper class | Data access |
| `@Entity` | Table creation SQL | Schema |
| `@Query` | `rdbStore.query()` | Queries |

### 9. Async/Reactive Mapping

| Android (RxJava) | ArkTS | Notes |
|---|---|---|
| `Observable.create()` | `async/await` or `Promise` | Async pattern |
| `.subscribeOn(Schedulers.io())` | Use `taskpool` or `worker` | Background thread |
| `.observeOn(mainThread)` | UI updates auto on main thread | No need |
| `.subscribe()` | `await` or `.then()` | Consume result |
| `EventBus.post()` | `Emitter` or `@State` change | Event system |
| `@Subscribe` | `Emitter.on()` listener | Event listener |

### 10. Resource Mapping

| Android Resource | ArkTS Resource | Notes |
|---|---|---|
| `res/layout/*.xml` | Declarative code | No XML layouts |
| `res/values/strings.xml` | `resources/base/element/string.json` | Strings |
| `res/drawable/*` | `resources/base/media/*` | Images |
| `res/color/*` | `resources/base/element/color.json` | Colors |
| `res/dimens.xml` | `resources/base/element/dimen.json` | Dimensions |
| `R.string.xxx` | `$r('app.string.xxx')` | String ref |
| `R.drawable.xxx` | `$r('app.media.xxx')` | Media ref |
| `R.color.xxx` | `$r('app.color.xxx')` | Color ref |
| `R.dimen.xxx` | `$r('app.float.xxx')` | Dimension ref |

## Conversion Process Steps

### Step 1: Project Structure Setup
1. Create HarmonyOS project structure
2. Configure `build-profile.json5`, `module.json5`
3. Set up resource directories
4. Configure dependencies

### Step 2: Convert Data Models
1. Convert Java POJOs to ArkTS classes
2. Replace Java types with TypeScript types
3. Remove Parcelable/Serializable, use JSON
4. Convert getters/setters to properties

### Step 3: Convert Business Logic
1. Replace RxJava with async/await
2. Replace EventBus with Emitter/@State
3. Convert static utility methods
4. Adapt database layer to RDB

### Step 4: Convert UI Layer
1. Convert XML layouts to declarative UI
2. Convert Activities to @Entry @Component
3. Convert Fragments to @Component
4. Convert RecyclerView to List + LazyForEach
5. Replace ViewBinding with direct property access

### Step 5: Convert System Integration
1. Convert Services to ServiceExtensionAbility
2. Convert BroadcastReceivers to CommonEvent
3. Replace WorkManager with workScheduler
4. Convert notifications

### Step 6: Testing & Verification
1. Verify compilation
2. Run on emulator/device
3. Fix runtime issues
4. Verify all features work

## Key ArkTS Syntax Patterns

### Basic Component
```typescript
@Component
struct MyComponent {
  @State message: string = 'Hello'

  build() {
    Column() {
      Text(this.message)
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
      Button('Click me')
        .onClick(() => {
          this.message = 'Clicked!'
        })
    }
    .width('100%')
    .height('100%')
  }
}
```

### Entry Component (Page)
```typescript
@Entry
@Component
struct MainPage {
  build() {
    Column() {
      // page content
    }
  }
}
```

### List with LazyForEach
```typescript
@Component
struct MyList {
  private data: MyDataSource = new MyDataSource()

  build() {
    List() {
      LazyForEach(this.data, (item: ItemData) => {
        ListItem() {
          Text(item.title)
        }
      }, (item: ItemData) => item.id)
    }
  }
}
```

### Navigation
```typescript
// Navigation setup
Navigation() {
  // content
}
.navDestination(this.pageMap)
.navBarVisibility(BarVisibility.Auto)

// Push to new page
router.pushUrl({ url: 'pages/DetailPage', params: { id: 123 } })

// Get params
const params = router.getParams() as Record<string, number>
const id = params['id']
```

### Custom Dialog
```typescript
@CustomDialog
struct MyDialog {
  controller: CustomDialogController
  @State input: string = ''

  build() {
    Column() {
      TextInput({ text: this.input })
      Button('OK')
        .onClick(() => {
          this.controller.close()
        })
    }
  }
}
```

### Preferences
```typescript
import { dataPreferences } from '@kit.ArkData'

const store = await dataPreferences.getPreferences(context, 'myStore')
await store.put('key', 'value')
const value = await store.get('key', '')
await store.flush()
```

### HTTP Request
```typescript
import { http } from '@kit.NetworkKit'

const httpRequest = http.createHttp()
const response = await httpRequest.request(url, {
  method: http.RequestMethod.GET,
  header: { 'Content-Type': 'application/json' }
})
const data = JSON.parse(response.result as string)
httpRequest.destroy()
```

### RDB Database
```typescript
import { dataRdb } from '@kit.ArkData'

const STORE_CONFIG: dataRdb.StoreConfig = {
  name: 'mydb.db',
  securityLevel: dataRdb.SecurityLevel.S1
}
const rdbStore = await dataRdb.getRdbStore(context, STORE_CONFIG)

// Insert
const valueBucket: dataRdb.ValuesBucket = {
  'name': 'test',
  'age': 25
}
const rowId = await rdbStore.insert('users', valueBucket)

// Query
const predicates = new dataRdb.RdbPredicates('users')
predicates.equalTo('name', 'test')
const resultSet = await rdbStore.query(predicates, ['id', 'name', 'age'])
while (resultSet.goToNextRow()) {
  const name = resultSet.getString(resultSet.getColumnIndex('name'))
}
resultSet.close()
```

### Worker Thread
```typescript
import { worker } from '@kit.CoreServicesKit'

const myWorker = new worker.ThreadWorker('workers/MyWorker.ts')
myWorker.postMessage({ data: 'process this' })
myWorker.onmessage = (e) => {
  const result = e.data
}
```

## Conversion Checklist

For each file being converted:
- [ ] Replace Java types with TypeScript types
- [ ] Convert class syntax (remove semicolons, add type annotations)
- [ ] Replace Android imports with ArkTS imports
- [ ] Convert XML layouts to declarative UI code
- [ ] Replace lifecycle methods
- [ ] Convert async patterns (RxJava → async/await)
- [ ] Replace EventBus with Emitter or @State
- [ ] Convert database access to RDB
- [ ] Replace resource references
- [ ] Convert navigation patterns
- [ ] Add proper type annotations
- [ ] Verify no Android-specific APIs remain
