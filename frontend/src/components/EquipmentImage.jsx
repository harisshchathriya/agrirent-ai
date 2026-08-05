import { FaTractor } from "react-icons/fa";

export default function EquipmentImage({
  src,
  alt,
  className = "",
  iconClassName = "text-6xl text-emerald-700",
  containerClassName = "",
}) {
  return (
    <div
      className={`flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50 ${containerClassName}`}
    >
      {src ? (
        <img
          src={src}
          alt={alt}
          className={`h-full w-full object-cover ${className}`}
        />
      ) : (
        <FaTractor className={iconClassName} />
      )}
    </div>
  );
}
